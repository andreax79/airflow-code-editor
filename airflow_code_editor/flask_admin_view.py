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

from flask_admin import BaseView, expose
import airflow
from airflow.utils.db import provide_session
from airflow_code_editor.code_editor_view import AbstractCodeEditorView
from airflow_code_editor.auth import login_required
from airflow_code_editor.commons import (
    ROUTE,
    MENU_CATEGORY,
    MENU_LABEL
)
assert(airflow)

__all__ = [
    'AdminCodeEditorView',
    'admin_view'
]


# ############################################################################
# Flask Admin

class AdminCodeEditorView(BaseView, AbstractCodeEditorView):

    @expose('/')
    @login_required
    @provide_session
    def index(self, session=None):
        return self._index(session)

    @expose('/editor', methods=['GET', 'POST'])
    @login_required
    @provide_session
    def editor_base(self, session=None):
        return self._editor(session)

    @expose('/editor/<path:path>', methods=['GET', 'POST'])
    @login_required
    @provide_session
    def editor(self, session=None, path=None):
        return self._editor(session, path)

    @expose('/repo', methods=['POST'])
    @login_required
    @provide_session
    def repo_base(self, session=None, path=None):
        return self._git_repo(session, path)

    @expose('/repo/<path:path>', methods=['GET', 'HEAD', 'POST'])
    @login_required
    @provide_session
    def repo(self, session=None, path=None):
        return self._git_repo(session, path)

    @expose('/download/<path:path>', methods=['GET'])
    @login_required
    @provide_session
    def download(self, session=None, path=None):
        return self._download(session, path)

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
