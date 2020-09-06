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
__version__ = '2.2.2'

from flask import Blueprint
from airflow.plugins_manager import AirflowPlugin
from airflow_code_editor.commons import STATIC
from airflow_code_editor.flask_admin_view import admin_view
from airflow_code_editor.app_builder_view import appbuilder_view

__all__ = [
    'CodeEditorPlugin'
]


code_editor_plugin_blueprint = Blueprint(
    'code_editor_plugin_blueprint',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path=STATIC
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
