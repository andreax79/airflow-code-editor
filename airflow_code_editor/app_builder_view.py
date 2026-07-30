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
from functools import wraps

from airflow.plugins_manager import AirflowPlugin
from airflow.www.extensions.init_auth_manager import get_auth_manager
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
from airflow_code_editor.git import is_readonly_git_command
from airflow_code_editor.utils import forbidden, is_enabled

__all__ = [
    "appbuilder_view",
    "api_reference_menu",
    "api_blueprint",
    "flask_blueprints",
    "CodeEditorPlugin",
]


# ############################################################################
# AppBuilder (Airflow 2.x)


def has_access(method, check_git_command=False):
    "Decorator to check if the user has access for the given method"

    def has_access_decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            auth_manager = get_auth_manager()
            if not get_auth_manager().is_logged_in():
                return forbidden()
            if not auth_manager.is_authorized_dag(method=method):
                return forbidden()
            if check_git_command:
                git_args = request.json.get("args", [])
                can_edit = auth_manager.is_authorized_dag(method="PUT")
                if not can_edit and not is_readonly_git_command(git_args):
                    return forbidden()
            return func(*args, **kwargs)

        return decorated

    return has_access_decorator


class AppBuilderCodeEditorView(BaseView):
    route_base = ROUTE
    base_permissions = ["can_list", "can_create", "menu_acccess"]

    @expose("/")
    @has_access(method="GET")
    def list(self):
        return self.render_template(
            "index_appbuilder.html",
            airflow_major_version=2,  # Airflow 2
            js_files=JS_FILES,
            version=VERSION,
        )

    @expose("/api/")
    @has_access(method="GET")
    def api(self):
        return redirect(request.path + "/ui")

    @expose("/repo", methods=["POST"])
    @has_access(method="GET", check_git_command=True)
    def repo_base(self):
        git_args = request.json.get("args", [])
        return api.execute_git_command(git_args)

    @expose("/files/<path:path>", methods=["POST"])
    @has_access(method="PUT")
    def save(self, path=None):
        mime_type = request.headers.get("Content-Type", "text/plain")
        data = request.get_data()
        return api.save(path=path, data=data, mime_type=mime_type)

    @expose("/files/<path:path>", methods=["GET"])
    @has_access(method="GET")
    def load(self, path=None):
        return api.load(path)

    @expose("/files/<path:path>", methods=["DELETE"])
    @has_access(method="DELETE")
    def delete(self, path=None):
        return api.delete(path)

    @expose("/format", methods=["POST"])
    @has_access(method="PUT")
    def format(self):
        data = request.get_data(as_text=True)
        return api.format(data)

    @expose("/tree", methods=["GET", "HEAD"])
    @has_access(method="GET")
    def tree_base(self, path=None):
        return api.tree(path, args=request.args, method=request.method)

    @expose("/tree/<path:path>", methods=["GET", "HEAD"])
    @has_access(method="GET")
    def tree(self, path=None):
        return api.tree(path, args=request.args, method=request.method)

    @expose("/search", methods=["GET"])
    @has_access(method="GET")
    def search(self):
        return api.search(args=request.args)

    @expose("/version", methods=["GET"])
    @has_access(method="GET")
    def get_version(self):
        return api.get_version()

    @expose("/permissions", methods=["GET"])
    @has_access(method="GET")
    def get_permissions(self):
        "Get the current user permissions"
        can_edit = get_auth_manager().is_authorized_dag(method="PUT")
        return {
            "can_edit": can_edit,
        }

    @expose("/ping", methods=["GET"])
    @has_access(method="GET")
    def ping(self):
        return api.ping()

    @expose("/generate_presigned", methods=["POST"])
    @has_access(method="GET")
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
