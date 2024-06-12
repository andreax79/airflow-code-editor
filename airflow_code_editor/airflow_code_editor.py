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

from airflow.plugins_manager import AirflowPlugin
from flask import Blueprint

try:
    from airflow_code_editor.api import api_blueprint
except Exception:
    api_blueprint = None

from airflow_code_editor.app_builder_view import api_reference_menu, appbuilder_view
from airflow_code_editor.commons import STATIC, VERSION
from airflow_code_editor.flask_admin_view import admin_view
from airflow_code_editor.utils import is_enabled

__author__ = 'Andrea Bonomi <andrea.bonomi@gmail.com>'
__version__ = VERSION

__all__ = ['CodeEditorPlugin']


# Blueprints
code_editor_plugin_blueprint = Blueprint(
    'code_editor_plugin_blueprint',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path=STATIC,
)
flask_blueprints = [code_editor_plugin_blueprint]
if api_blueprint is not None:
    flask_blueprints.append(api_blueprint)


# Plugin
class CodeEditorPlugin(AirflowPlugin):
    name = 'editor_plugin'
    operators = []
    flask_blueprints = flask_blueprints
    hooks = []
    executors = []
    admin_views = [admin_view] if (is_enabled() and admin_view is not None) else []
    menu_links = []
    appbuilder_menu_items = [api_reference_menu] if (is_enabled() and api_blueprint is not None) else []
    appbuilder_views = [appbuilder_view] if is_enabled() else []
