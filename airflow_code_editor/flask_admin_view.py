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

import airflow
from functools import wraps
from airflow_code_editor.code_editor_view import AbstractCodeEditorView
from airflow_code_editor.commons import ROUTE, MENU_CATEGORY, MENU_LABEL, JS_FILES

__all__ = ["admin_view"]

# ############################################################################
# Flask Admin (Airflow < 2.0 and rbac = False)

try:
    from flask_admin import BaseView, expose

    def login_required(func):
        # when airflow loads plugins, login is still None.
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            if airflow.login:
                return airflow.login.login_required(func)(*args, **kwargs)
            return func(*args, **kwargs)

        return func_wrapper

    class AdminCodeEditorView(BaseView, AbstractCodeEditorView):
        @expose("/")
        @login_required
        def index(self):
            return self._index()

        @expose("/repo", methods=["POST"])
        @login_required
        def repo_base(self, path=None):
            return self._git_repo(path)

        @expose("/repo/<path:path>", methods=["GET", "HEAD", "POST"])
        @login_required
        def repo(self, path=None):
            return self._git_repo(path)

        @expose("/files/<path:path>", methods=["POST"])
        @login_required
        def save(self, path=None):
            return self._save(path)

        @expose("/files/<path:path>", methods=["GET"])
        @login_required
        def load(self, path=None):
            return self._load(path)

        @expose("/format", methods=["GET"])
        @login_required
        def format(self, path=None):
            return self._load(path)

        def _render(self, template, *args, **kargs):
            return self.render(
                template + "_admin.html",
                airflow_major_version=self.airflow_major_version,
                js_files=JS_FILES,
                *args,
                **kargs
            )

    admin_view = AdminCodeEditorView(url=ROUTE, category=MENU_CATEGORY, name=MENU_LABEL)

except (ImportError, ModuleNotFoundError):
    admin_view = None
