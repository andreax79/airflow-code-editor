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
#   limitations under the License
#

from airflow.plugins_manager import AirflowPlugin

from airflow_code_editor.app_builder_view import (
    api_blueprint,
    api_reference_menu,
    appbuilder_view,
    flask_blueprints,
)
from airflow_code_editor.commons import VERSION
from airflow_code_editor.utils import is_enabled

__author__ = 'Andrea Bonomi <andrea.bonomi@gmail.com>'
__version__ = VERSION

__all__ = ['CodeEditorPlugin']


# Plugin
class CodeEditorPlugin(AirflowPlugin):
    name = 'editor_plugin'
    operators = []
    flask_blueprints = flask_blueprints
    hooks = []
    executors = []
    admin_views = []
    menu_links = []
    appbuilder_menu_items = [api_reference_menu] if (is_enabled() and api_blueprint is not None) else []
    appbuilder_views = [appbuilder_view] if is_enabled() else []
    fastapi_apps = []
