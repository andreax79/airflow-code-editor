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

from airflow.version import version as airflow_version
from flask import make_response, request
from flask_wtf.csrf import generate_csrf
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename

from airflow_code_editor.commons import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_SERVER_ERROR,
    VERSION,
)
from airflow_code_editor.fs import RootFS
from airflow_code_editor.git import execute_git_command
from airflow_code_editor.tree import get_stat, get_tree
from airflow_code_editor.utils import (
    DummyLexer,
    error_message,
    get_plugin_boolean_config,
    get_plugin_int_config,
    normalize_path,
    prepare_api_response,
)

__all__ = ["AbstractCodeEditorView"]

AIRFLOW_MAJOR_VERSION = int(airflow_version.split(".")[0])


class AbstractCodeEditorView(object):
    airflow_major_version = AIRFLOW_MAJOR_VERSION

    def _index(self):
        return self._render("index")

    @classmethod
    def _save(cls, path=None):
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
                http_status_code=HTTP_400_BAD_REQUEST,
                error_message="Error saving {path}: {message}".format(path=path, message=error_message(ex)),
            )

    @classmethod
    def _git_repo_get(cls, path):
        "Get a file from GIT (invoked by the HTTP GET method)"
        try:
            # Download git blob - path = '<hash>/<name>'
            path, attachment_filename = path.split("/", 1)
        except Exception:
            # No attachment filename
            attachment_filename = None
        response = execute_git_command(["cat-file", "-p", path]).prepare_git_response()
        if attachment_filename:
            content_disposition = 'attachment; filename="{0}"'.format(attachment_filename)
            response.headers["Content-Disposition"] = content_disposition
            try:
                content_type = mimetypes.guess_type(attachment_filename)[0]
                if content_type:
                    response.headers["Content-Type"] = content_type
            except Exception:
                pass
        return response

    @classmethod
    def _execute_git_command(cls):
        "Execute a GIT command (invoked by the HTTP POST method)"
        git_args = request.json.get("args", [])
        return execute_git_command(git_args).prepare_git_response()

    @classmethod
    def _load(cls, path):
        "Send the contents of a file to the client"
        try:
            path = normalize_path(path)
            if path.startswith("~git/"):
                # Download git blob - path = '~git/<hash>/<name>'
                _, path = path.split("/", 1)
                return cls._git_repo_get(path)
            else:
                # Download file
                root_fs = RootFS()
                return root_fs.path(path).send_file(as_attachment=True)
        except Exception as ex:
            logging.error(ex)
            strerror = getattr(ex, "strerror", str(ex))
            errno = getattr(ex, "errno", 0)
            return prepare_api_response(
                error_message=strerror,
                errno=errno,
                http_status_code=HTTP_404_NOT_FOUND,
            )

    @classmethod
    def _delete(cls, path):
        "Delete a file"
        path = normalize_path(path)
        if path.startswith("~git/"):
            # Git files cannot be deleted
            return prepare_api_response(
                error_message="Permission denied",
                http_status_code=HTTP_400_BAD_REQUEST,
            )
        try:
            # Delete the file
            root_fs = RootFS()
            root_fs.path(path).delete()
            return prepare_api_response(message="File deleted")
        except FileNotFoundError:
            return prepare_api_response(
                error_message="File not found",
                http_status_code=HTTP_404_NOT_FOUND,
            )
        except Exception as ex:
            return prepare_api_response(
                error_message=str(ex),
                http_status_code=HTTP_400_BAD_REQUEST,
            )

    @classmethod
    def _format(cls):
        "Sort imports and format code"
        try:
            import black
        except ImportError:
            black = None
        try:
            import isort
        except ImportError:
            isort = None
        if black is None and isort is None:
            return prepare_api_response(
                http_status_code=HTTP_500_SERVER_ERROR,
                error_message="black and isort dependencies are not installed."
                + "To install black and isort, use the following command: `pip install black isort`",
            )
        try:
            data = request.get_data(as_text=True)
            # Newline fix (remove cr)
            data = data.replace("\r", "").rstrip()
            # Sort imports
            if isort is not None:
                data = isort.code(data, profile="black")
            # Format
            if black is not None:
                mode = black.Mode(
                    string_normalization=get_plugin_boolean_config("string_normalization"),
                    line_length=get_plugin_int_config("line_length"),
                )
                data = black.format_str(src_contents=data, mode=mode)
            return prepare_api_response(data=data)
        except Exception as ex:
            logging.error(ex)
            return prepare_api_response(
                error_message="Error formatting: {message}".format(message=error_message(ex)),
                http_status_code=HTTP_400_BAD_REQUEST,
            )

    @classmethod
    def _tree(cls, path, args={}, method="GET"):
        try:
            if method == "HEAD":
                stat = get_stat(path)
                response = make_response("OK", HTTP_200_OK)
                response.headers["X-Id"] = stat["id"]
                response.headers["X-Leaf"] = "true" if stat["leaf"] else "false"
                response.headers["X-Exists"] = "true" if stat["exists"] else "false"
                return response
            else:
                return prepare_api_response(value=get_tree(path, args))
        except Exception as ex:
            logging.error(ex)
            return prepare_api_response(
                value=[],
                http_status_code=HTTP_500_SERVER_ERROR,
                error_message="Error: {message}".format(message=error_message(ex)),
            )

    @classmethod
    def _search(cls, args={}):
        "File search"
        query = args.get("query")
        root_fs = RootFS()
        result = []
        context_ = args.get('context') == 'true'  # include context in results
        for match in root_fs.search(query=query):
            if context_:
                formatter = HtmlFormatter(
                    linenos=True,
                    cssclass="source",
                    nobackground=True,
                    linenostart=match["context_first_row"],
                    hl_lines=[match["row_number"] - match["context_first_row"] + 1],
                )
                try:
                    lexer = get_lexer_for_filename(match["path"])
                except Exception:
                    lexer = DummyLexer()
                try:
                    context = highlight(match["context"], lexer, formatter)
                except Exception:
                    context = match["context"]
                result.append({"row_number": match["row_number"], "context": context, "path": match["path"]})
            else:
                result.append({"row_number": match["row_number"], "path": match["path"]})
        return prepare_api_response(value=result)

    @classmethod
    def _ping(cls):
        return {"value": generate_csrf()}

    @classmethod
    def _get_version(cls):
        "Get version information"
        return {
            "version": VERSION,
            "airflow_version": airflow_version,
        }
