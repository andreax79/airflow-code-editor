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
from flask import request
from flask_wtf.csrf import generate_csrf
from airflow.version import version
from airflow_code_editor import tree
from airflow_code_editor.utils import (
    get_plugin_boolean_config,
    get_plugin_int_config,
    execute_git_command,
    error_message,
    prepare_api_response,
)


__all__ = ["AbstractCodeEditorView"]

AIRFLOW_MAJOR_VERSION = int(version.split(".")[0])


class AbstractCodeEditorView(object):
    airflow_major_version = AIRFLOW_MAJOR_VERSION

    def _index(self):
        return self._render("index")

    def _save(self, path=None):
        mime_type = request.headers.get("Content-Type", "text/plain")
        return tree.post(path, mime_type=mime_type)

    def _git_repo_post(self, path):
        " Execute a GIT command (invoked by the HTTP POST method) "
        git_args = request.json.get('args', [])
        return execute_git_command(git_args)

    def _load(self, path):
        " Send the contents of a file to the client "
        return tree.get(path, as_attachment=True)

    def _format(self):
        " Format code "
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
        return {'value': tree.get_tree(path, args)}

    def _ping(self):
        return {'value': generate_csrf()}
