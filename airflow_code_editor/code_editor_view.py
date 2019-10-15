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

import os
import os.path
import logging
from flask import request, flash
from airflow import configuration
from airflow.models.errors import ImportError
from airflow_code_editor.commons import ROUTE
from airflow_code_editor.utils import (
    normalize_path,
    execute_git_command
)

__all__ = [
    'AbstractCodeEditorView'
]

class AbstractCodeEditorView(object):

    def _index(self, session=None):
        return self._render('index')

    def _load(self, path):
        try:
            code = None
            cwd = configuration.get('core', 'dags_folder')
            fullpath = os.path.join(cwd, path)
            # Read code
            with open(fullpath, 'r') as f:
                code = f.read().rstrip('\n')
        except Exception as ex:
            logging.error(ex)
            flash('Error loading file [{path}]'.format(path=path),
                  'error')
        finally:
            return code

    def _save(self, path):
        try:
            code = None
            code = request.form['code']
            # Newline fix (remove cr)
            code = code.replace('\r', '').rstrip()
            cwd = configuration.get('core', 'dags_folder')
            fullpath = os.path.join(cwd, path)
            with open(fullpath, 'w') as f:
                f.write(code)
                f.write('\n')
            flash('File [{path}] saved successfully'.format(path=path),
              'success')
        except Exception as ex:
            logging.error(ex)
            flash('Error saving file [{path}]'.format(path=path),
                  'error')
        finally:
            return code

    def _editor(self, session=None, path=None):
        path = normalize_path(path)
        try:
            code = None
            # Display import error
            for ie in session.query(ImportError).all():
                if ie.filename == path:
                    flash('Broken DAG: [{ie.filename}] {ie.stacktrace}'.format(ie=ie),
                          'dag_import_error')
            # Load or Save DAG
            if 'code' in request.form:
                code = self._save(path)
            else:
                code = self._load(path)
        finally:
            return self._render(
                'editor',
                code=code,
                path=path,
                back=ROUTE,
                root=request.args.get('root'))

    def _git_repo(self, session, path):
        if request.method == 'POST':
            return self._git_repo_post(session, path)
        else:
            return self._git_repo_get(session, path)

    def _git_repo_get(self, session, path):
        " Get a file from GIT (invoked by the HTTP GET method) "
        return execute_git_command([ "cat-file", "-p", path ])

    def _git_repo_post(self, session, path):
        " Execute a GIT command (invoked by the HTTP POST method) "
        git_args = request.form.getlist('args[]')
        return execute_git_command(git_args)

