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
import mimetypes
from flask import abort, jsonify, request, send_file
from airflow.version import version
from airflow_code_editor.commons import HTTP_404_NOT_FOUND
from airflow_code_editor.utils import (
    git_absolute_path,
    execute_git_command,
    normalize_path,
)

__all__ = ['AbstractCodeEditorView']

AIRFLOW_MAJOR_VERSION = int(version.split('.')[0])


class AbstractCodeEditorView(object):
    airflow_major_version = AIRFLOW_MAJOR_VERSION

    def _index(self):
        return self._render('index')

    def _save(self, path=None):
        try:
            data = request.form['data']
            # Newline fix (remove cr)
            data = data.replace('\r', '').rstrip()
            fullpath = git_absolute_path(path)
            os.makedirs(os.path.dirname(fullpath), exist_ok=True)
            with open(fullpath, 'w') as f:
                f.write(data)
                f.write('\n')
            return jsonify({'path': normalize_path(path)})
        except Exception as ex:
            logging.error(ex)
            if hasattr(ex, 'strerror'):
                message = ex.strerror
            elif hasattr(ex, 'message'):
                message = ex.message
            else:
                message = str(ex)
            return jsonify(
                {
                    'path': normalize_path(path),
                    'error': {
                        'message': 'Error saving {path}: {message}'.format(
                            path=path, message=message
                        )
                    },
                }
            )

    def _git_repo(self, path):
        if request.method == 'POST':
            return self._git_repo_post(path)
        else:
            return self._git_repo_get(path)

    def _git_repo_get(self, path):
        " Get a file from GIT (invoked by the HTTP GET method) "
        return execute_git_command(["cat-file", "-p", path])

    def _git_repo_post(self, path):
        " Execute a GIT command (invoked by the HTTP POST method) "
        git_args = request.form.getlist('args[]')
        return execute_git_command(git_args)

    def _load(self, path):
        " Send the contents of a file to the client "
        try:
            path = normalize_path(path)
            if path.startswith('~git/'):
                # Download git blob - path = '~git/<hash>/<name>'
                _, path, filename = path.split('/', 3)
                response = execute_git_command(["cat-file", "-p", path])
                response.headers['Content-Disposition'] = (
                    'attachment; filename="%s"' % filename
                )
                try:
                    content_type = mimetypes.guess_type(filename)[0]
                    if content_type:
                        response.headers['Content-Type'] = content_type
                except Exception:
                    pass
                return response
            else:
                # Download file
                fullpath = git_absolute_path(path)
                return send_file(fullpath, as_attachment=True)
        except Exception as ex:
            logging.error(ex)
            abort(HTTP_404_NOT_FOUND)
