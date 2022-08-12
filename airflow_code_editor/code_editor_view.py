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

import logging
import mimetypes
from flask import request, make_response
from flask_wtf.csrf import generate_csrf
from airflow.version import version
from airflow_code_editor.commons import HTTP_404_NOT_FOUND
from airflow_code_editor.tree import get_tree
from airflow_code_editor.utils import (
    get_plugin_boolean_config,
    get_plugin_int_config,
    error_message,
    normalize_path,
    prepare_api_response,
)
from airflow_code_editor.git import (
    execute_git_command,
)
from airflow_code_editor.fs import RootFS


__all__ = ["AbstractCodeEditorView"]

AIRFLOW_MAJOR_VERSION = int(version.split(".")[0])


class AbstractCodeEditorView(object):
    airflow_major_version = AIRFLOW_MAJOR_VERSION

    def _index(self):
        return self._render("index")

    def _save(self, path=None):
        try:
            mime_type = request.headers.get("Content-Type", "text/plain")
            is_text = mime_type.startswith("text/")
            if is_text:
                data = request.get_data(as_text=True)
                # Newline fix (remove cr)
                data = data.replace("\r", "").rstrip() + "\n"
            else:  # Binary file
                data = request.get_data()
            root_fs = RootFS()
            root_fs.path(path).write_file(data=data, is_text=is_text)
            return prepare_api_response(path=normalize_path(path))
        except Exception as ex:
            logging.error(ex)
            return prepare_api_response(
                path=normalize_path(path),
                error_message="Error saving {path}: {message}".format(
                    path=path, message=error_message(ex)
                ),
            )

    def _git_repo(self, path):
        if request.method == "POST":
            return self._git_repo_post(path)
        else:
            return self._git_repo_get(path)

    def _git_repo_get(self, path):
        "Get a file from GIT (invoked by the HTTP GET method)"
        try:
            # Download git blob - path = '<hash>/<name>'
            path, attachment_filename = path.split('/', 1)
        except Exception:
            # No attachment filename
            attachment_filename = None
        response = execute_git_command(["cat-file", "-p", path])
        if attachment_filename:
            response.headers[
                "Content-Disposition"
            ] = 'attachment; filename="{0}"'.format(attachment_filename)
            try:
                content_type = mimetypes.guess_type(attachment_filename)[0]
                if content_type:
                    response.headers["Content-Type"] = content_type
            except Exception:
                pass
        return response

    def _git_repo_post(self, path):
        "Execute a GIT command (invoked by the HTTP POST method)"
        git_args = request.json.get('args', [])
        return execute_git_command(git_args)

    def _load(self, path):
        "Send the contents of a file to the client"
        try:
            path = normalize_path(path)
            if path.startswith("~git/"):
                # Download git blob - path = '~git/<hash>/<name>'
                _, path = path.split("/", 1)
                return self._git_repo_get(path)
            else:
                # Download file
                root_fs = RootFS()
                return root_fs.path(path).send_file(as_attachment=True)
        except Exception as ex:
            logging.error(ex)
            strerror = getattr(ex, 'strerror', str(ex))
            errno = getattr(ex, 'errno', 0)
            message = prepare_api_response(error_message=strerror, errno=errno)
            return make_response(message, HTTP_404_NOT_FOUND)

    def _format(self):
        "Format code"
        try:
            import black

            data = request.get_data(as_text=True)
            # Newline fix (remove cr)
            data = data.replace("\r", "").rstrip()
            mode = black.Mode(
                string_normalization=get_plugin_boolean_config("string_normalization"),
                line_length=get_plugin_int_config("line_length"),
            )
            data = black.format_str(src_contents=data, mode=mode)
            return prepare_api_response(data=data)
        except ImportError:
            return prepare_api_response(
                error_message="black dependency is not installed: to install black `pip install black`"
            )
        except Exception as ex:
            logging.error(ex)
            return prepare_api_response(
                error_message="Error formatting: {message}".format(
                    message=error_message(ex)
                )
            )

    def _tree(self, path, args={}):
        return {'value': get_tree(path, args)}

    def _ping(self):
        return {'value': generate_csrf()}
