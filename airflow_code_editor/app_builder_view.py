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

from flask_appbuilder import BaseView, expose
from airflow.utils.db import provide_session
from airflow.www_rbac.decorators import has_dag_access
from airflow_code_editor.auth import has_access
from airflow_code_editor.code_editor_view import AbstractCodeEditorView
from airflow_code_editor.commons import (
    ROUTE,
    MENU_CATEGORY,
    MENU_LABEL
)

__all__ = [
    'AppBuilderCodeEditorView',
    'appbuilder_view'
]


# ############################################################################
# AppBuilder (Airflow >= 1.10 and rbac = True)

class AppBuilderCodeEditorView(BaseView, AbstractCodeEditorView):
    route_base = ROUTE
    base_permissions = ['can_list']

    @expose('/')
    @has_dag_access(can_dag_edit=True)
    @has_access
    @provide_session
    def list(self, session=None):
        return self._index(session)

    @expose('/editor', methods=['GET', 'POST'])
    @has_dag_access(can_dag_edit=True)
    @provide_session
    def editor_base(self, session=None):
        return self._editor(session)

    @expose('/editor/<path:path>', methods=['GET', 'POST'])
    @has_dag_access(can_dag_edit=True)
    @provide_session
    def editor(self, session=None, path=None):
        return self._editor(session, path)

    @expose('/repo', methods=['POST'])
    @has_dag_access(can_dag_edit=True)
    @provide_session
    def repo_base(self, session=None, path=None):
        return self._git_repo(session, path)

    @expose('/repo/<path:path>', methods=['GET', 'HEAD', 'POST'])
    @has_dag_access(can_dag_edit=True)
    @provide_session
    def repo(self, session=None, path=None):
        return self._git_repo(session, path)

    @expose('/download/<path:path>', methods=['GET'])
    @has_dag_access(can_dag_edit=True)
    @provide_session
    def download(self, session=None, path=None):
        return self._download(session, path)

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
