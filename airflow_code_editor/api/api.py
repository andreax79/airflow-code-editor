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

import logging
import mimetypes

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename

from airflow_code_editor import git
from airflow_code_editor.commons import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_500_SERVER_ERROR,
    VERSION,
)
from airflow_code_editor.fs import RootFS
from airflow_code_editor.presigned import create_presigned, decode_presigned
from airflow_code_editor.tree import get_stat, get_tree
from airflow_code_editor.utils import (
    DummyLexer,
    airflow_version,
    error_message,
    generate_csrf,
    get_plugin_boolean_config,
    get_plugin_int_config,
    make_response,
    normalize_path,
    prepare_api_response,
)

__all__ = [
    "save",
    "load",
    "delete",
    "format",
    "tree",
    "search",
    "ping",
    "get_version",
    "generate_presigned",
    "load_presigned",
]


def save(path: str, data: bytes, mime_type: str):
    "Save a file (invoked by the HTTP POST method)"
    try:
        is_text = mime_type.startswith("text/")
        if is_text:
            data = data.decode("utf-8", errors="ignore")
            # Newline fix (remove cr)
            data = data.replace("\r", "").rstrip() + "\n"
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


def git_repo_get(path):
    "Get a file from GIT (invoked by the HTTP GET method)"
    try:
        # Download git blob - path = '<hash>/<name>'
        path, attachment_filename = path.split("/", 1)
    except Exception:
        # No attachment filename
        attachment_filename = None
    response = execute_git_command(["cat-file", "-p", path])
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


def execute_git_command(git_args):
    "Execute a GIT command (invoked by the HTTP POST method)"
    return git.execute_git_command(git_args).prepare_git_response()


def load(path):
    "Send the contents of a file to the client"
    try:
        path = normalize_path(path)
        if path.startswith("~git/"):
            # Download git blob - path = '~git/<hash>/<name>'
            _, path = path.split("/", 1)
            return git_repo_get(path)
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


def delete(path):
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


def format(data: str):
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


def tree(path, args={}, method="GET"):
    "Get tree entries"
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


def search(args={}):
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


def ping():
    "Ping"
    return {"value": generate_csrf()}


def get_version():
    "Get version information"
    return {
        "version": VERSION,
        "airflow_version": airflow_version,
    }


def generate_presigned(path):
    "Generate a presigned URL token for downloading a file/git object"
    return {
        "token": create_presigned(path),
    }


def load_presigned(token: str):
    "Download a file/git object using a presigned URL"
    try:
        path = decode_presigned(token)
    except Exception as ex:
        logging.error(ex)
        return prepare_api_response(
            error_message="Not authenticated",
            http_status_code=HTTP_401_UNAUTHORIZED,
        )
    return load(path)
