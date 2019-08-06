#!/usr/bin/env python
#
#   Copyright 2019 Andrea Bonomi <andrea.bonomi@gmail.com>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the Licens
#
__author__ = 'Andrea Bonomi <andrea.bonomi@gmail.com>'
__version__ = '1.0.0'

import os
import os.path
import logging
from flask import Blueprint, request, flash
import flask_admin
import flask_appbuilder
import airflow
from airflow.plugins_manager import AirflowPlugin
from airflow.models import DagModel
from airflow.models.errors import ImportError
from airflow.utils.db import provide_session
from airflow.exceptions import DagNotFound
from airflow.www_rbac.utils import open_maybe_zipped
from airflow.www_rbac.decorators import has_dag_access
try:
    from flask_appbuilder import has_access
except:
    has_access = lambda x: x

CONFIG_SECTION = 'editor_plugin'
MENU_CATEGORY = 'Admin'
MENU_LABEL = 'DAGs Code Editor'
ROUTE = '/code_editor'

__all__ = [
    'CodeEditorPlugin'
]

class AbstractCodeEditorView(object):

    def _index(self, session=None):
        for ie in session.query(ImportError).all():
            flash('Broken DAG: [{ie.filename}] {ie.stacktrace}'.format(ie=ie),
                  'dag_import_error')
        dags = session.query(DagModel).all()
        return self._render('index', dags=dags)

    def _parse_args(self, session):
        # Get DAG
        code = None
        dag_id = request.args.get('dag_id')
        dag = (session.query(DagModel)
                      .filter(DagModel.dag_id == dag_id)
                      .first())
        if dag is None:
            raise DagNotFound
        return dag_id, dag, code

    def _load(self, dag):
        try:
            code = None
            # Read code
            with open_maybe_zipped(dag.fileloc, 'r') as f:
                code = f.read()
        except Exception as ex:
            logging.error(ex)
            flash('Error loading DAG [{dag.dag_id}]'.format(dag=dag),
                  'error')
        finally:
            return code

    def _save(self, dag):
        try:
            code = None
            code = request.form['code']
            with open_maybe_zipped(dag.fileloc, 'w') as f:
                f.write(code)
                flash('DAG [{dag.dag_id}] saved successfully'.format(dag=dag),
                      'error')
        except Exception as ex:
            logging.error(ex)
            flash('Error saving DAG [{dag.dag_id}]'.format(dag=dag),
                  'error')
        finally:
            return code

    def _editor(self, session=None):
        try:
            code = None
            dag_id = None
            # Parse args and get DAG
            dag_id, dag, code = self._parse_args(session)
            # Display import error
            for ie in session.query(ImportError).all():
                if ie.filename == dag.fileloc:
                    flash('Broken DAG: [{ie.filename}] {ie.stacktrace}'.format(ie=ie),
                          'dag_import_error')
            # Load or Save DAG
            if 'code' in request.form:
                code = self._save(dag)
            else:
                code = self._load(dag)
        except DagNotFound:
            flash('DAG [{dag_id}] not found'.format(dag_id=dag_id),
                  'error')
            dag = None
        finally:
            return self._render(
                'editor',
                code=code,
                dag=dag,
                title=dag_id,
                back=ROUTE,
                root=request.args.get('root'))

# ############################################################################
# Flash Admin

if airflow.login is not None:
    login_required = airflow.login.login_required
else:
    login_required = lambda x: x

class AdminCodeEditorView(flask_admin.BaseView, AbstractCodeEditorView):

    @flask_admin.expose('/')
    @login_required
    @provide_session
    def index(self, session=None):
        return self._index(session)

    @flask_admin.expose('/editor', methods=['GET', 'POST'])
    @login_required
    @provide_session
    def editor(self, session=None):
        return self._editor(session)

    def _render(self, template, *args, **kargs):
        return self.render(template + '_admin.html',
                airflow_refresh="airflow.refresh",
                log_list='log.index_view',
                *args, **kargs)


admin_view = AdminCodeEditorView(
    url=ROUTE,
    category=MENU_CATEGORY,
    name=MENU_LABEL
)


# ############################################################################
# AppBuilder (Airflow >= 1.10 and rbac = True)

class AppBuilderCodeEditorView(flask_appbuilder.BaseView, AbstractCodeEditorView):
    template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    route_base = ROUTE
    base_permissions = ['can_list']

    @flask_appbuilder.expose('/')
    @has_dag_access(can_dag_edit=True)
    @has_access
    @provide_session
    def list(self, session=None):
        return self._index(session)

    @flask_appbuilder.expose('/editor', methods=['GET', 'POST'])
    @has_dag_access(can_dag_edit=True)
    @provide_session
    def editor(self, session=None):
        return self._editor(session)

    def _render(self, template, *args, **kargs):
        return self.render_template(template + '_appbuilder.html',
                airflow_refresh='Airflow.refresh',
                log_list='LogModelView.list',
                *args, **kargs)


appbuilder_code_editor_view = AppBuilderCodeEditorView()
appbuilder_view = {
    'category': MENU_CATEGORY,
    'name': MENU_LABEL,
    'view': appbuilder_code_editor_view
}


# ############################################################################
# Blueprint
code_editor_plugin_blueprint = Blueprint(
    'code_editor_plugin_blueprint',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/editor/'
)

# Plugin
class CodeEditorPlugin(AirflowPlugin):
    name = 'editor_plugin'
    operators = []
    flask_blueprints = [code_editor_plugin_blueprint]
    hooks = []
    executors = []
    admin_views = [admin_view]
    menu_links = []
    appbuilder_views = [appbuilder_view]

