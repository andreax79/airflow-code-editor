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
from airflow.security import permissions
from airflow.www import auth
from flask import Blueprint, redirect, request
from flask_appbuilder import BaseView, expose

from airflow_code_editor.api import api
from airflow_code_editor.api.flask_endpoints import api_blueprint
from airflow_code_editor.commons import (
    API_REFERENCE_LABEL,
    API_REFERENCE_MENU_CATEGORY,
    JS_FILES,
    MENU_CATEGORY,
    MENU_LABEL,
    ROUTE,
    STATIC,
    VERSION,
)
from airflow_code_editor.utils import is_enabled

__all__ = [
    "appbuilder_view",
    "api_reference_menu",
    "api_blueprint",
    "flask_blueprints",
    "CodeEditorPlugin",
]

PERMISSIONS = [
    (permissions.ACTION_CAN_READ, permissions.RESOURCE_WEBSITE),
]

# ############################################################################
# AppBuilder (Airflow 2.x)


class AppBuilderCodeEditorView(BaseView):
    route_base = ROUTE
    base_permissions = ["can_list", "can_create", "menu_acccess"]

    @expose("/")
    @auth.has_access(PERMISSIONS)
    def list(self):
        return self.render_template(
            "index_appbuilder.html",
            airflow_major_version=2,  # Airflow 2
            js_files=JS_FILES,
            version=VERSION,
        )

    @expose("/api/")
    @auth.has_access(PERMISSIONS)
    def api(self):
        return redirect(request.path + "/ui")

    @expose("/repo", methods=["POST"])
    @auth.has_access(PERMISSIONS)
    def repo_base(self):
        git_args = request.json.get("args", [])
        return api.execute_git_command(git_args)

    @expose("/files/<path:path>", methods=["POST"])
    @auth.has_access(PERMISSIONS)
    def save(self, path=None):
        mime_type = request.headers.get("Content-Type", "text/plain")
        data = request.get_data()
        return api.save(path=path, data=data, mime_type=mime_type)

    @expose("/files/<path:path>", methods=["GET"])
    @auth.has_access(PERMISSIONS)
    def load(self, path=None):
        return api.load(path)

    @expose("/files/<path:path>", methods=["DELETE"])
    @auth.has_access(PERMISSIONS)
    def delete(self, path=None):
        return api.delete(path)

    @expose("/format", methods=["POST"])
    @auth.has_access(PERMISSIONS)
    def format(self):
        data = request.get_data(as_text=True)
        return api.format(data)

    @expose("/tree", methods=["GET", "HEAD"])
    @auth.has_access(PERMISSIONS)
    def tree_base(self, path=None):
        return api.tree(path, args=request.args, method=request.method)

    @expose("/tree/<path:path>", methods=["GET", "HEAD"])
    @auth.has_access(PERMISSIONS)
    def tree(self, path=None):
        return api.tree(path, args=request.args, method=request.method)

    @expose("/search", methods=["GET"])
    @auth.has_access(PERMISSIONS)
    def search(self):
        return api.search(args=request.args)

    @expose("/version", methods=["GET"])
    @auth.has_access(PERMISSIONS)
    def get_version(self):
        return api.get_version()

    @expose("/ping", methods=["GET"])
    @auth.has_access(PERMISSIONS)
    def ping(self):
        return api.ping()

    @expose("/generate_presigned", methods=["POST"])
    @auth.has_access(PERMISSIONS)
    def generate_presigned(self):
        path = request.json.get("path", "")
        return api.generate_presigned(path)

    @expose("/presigned/<path:path>", methods=["GET"])
    # auth is not required for presigned URLs
    def load_presigned(self, path=None):
        "Download a file/git object using a presigned URL"
        return api.load_presigned(path)


appbuilder_code_editor_view = AppBuilderCodeEditorView()
appbuilder_view = {
    "category": MENU_CATEGORY,
    "name": MENU_LABEL,
    "view": appbuilder_code_editor_view,
}
api_reference_menu = {
    "name": API_REFERENCE_LABEL,
    "category": API_REFERENCE_MENU_CATEGORY,
    "href": ROUTE + "/api/",
}
code_editor_plugin_blueprint = Blueprint(
    'code_editor_plugin_blueprint',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path=STATIC,
)
flask_blueprints = [code_editor_plugin_blueprint, api_blueprint]


# Plugin
class CodeEditorPlugin(AirflowPlugin):
    name = 'editor_plugin'
    flask_blueprints = flask_blueprints
    appbuilder_menu_items = [api_reference_menu] if (is_enabled() and api_blueprint is not None) else []
    appbuilder_views = [appbuilder_view] if is_enabled() else []
    fastapi_apps = []
