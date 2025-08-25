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

import importlib.resources

from airflow.api_connexion import security
from airflow.configuration import conf
from airflow.utils.yaml import safe_load
from airflow.www.app import csrf
from connexion import FlaskApi
from flask import request

from airflow_code_editor.api import api

__all__ = [
    "get_tree",
    "get_tree_root",
    "get_files",
    "post_files",
    "delete_files",
    "search",
    "post_git",
    "get_version",
    "generate_presigned",
    "load_presigned",
    "load_specification",
    "api_blueprint",
]


@security.requires_access_dag("GET")
@csrf.exempt
def get_tree(*, path: str = None):
    "List tree entries"
    return api.tree(path, args=request.args, method="GET")


@security.requires_access_dag("GET")
@csrf.exempt
def get_tree_root():
    "List root tree entries"
    return api.tree(None, args=request.args, method="GET")


@security.requires_access_dag("GET")
@csrf.exempt
def get_files(*, path: str = None):
    "Get file content"
    return api.load(path)


@security.requires_access_dag("PUT")
@csrf.exempt
def post_files(*, path: str = None):
    "Write file content"
    mime_type = request.headers.get("Content-Type", "text/plain")
    data = request.get_data()
    return api.save(path=path, data=data, mime_type=mime_type)


@security.requires_access_dag("PUT")
@csrf.exempt
def delete_files(*, path: str = None):
    "Delete a file"
    return api.delete(path)


@security.requires_access_dag("GET")
@csrf.exempt
def search(*, query: str):
    "File search"
    return api.search(args=request.args)


@security.requires_access_dag("PUT")
@csrf.exempt
def post_git():
    "Execute a GIT command"
    git_args = request.json.get("args", [])
    return api.execute_git_command(git_args)


@security.requires_access_dag("GET")
@csrf.exempt
def get_version():
    "Get version information"
    return api.get_version()


@security.requires_access_dag("PUT")
@csrf.exempt
def generate_presigned(*, path: str = None):
    "Generate a presigned URL token for downloading a file/git object"
    path = request.json.get("path", "")
    return api.generate_presigned(path)


# security is not required for presigned URLs
@csrf.exempt
def load_presigned(*, token: str = None):
    "Download a file/git object using a presigned URL"
    return api.load_presigned(token)


def load_specification() -> dict:
    with importlib.resources.path("airflow_code_editor.api", "code_editor.yaml") as f:
        return safe_load(f.read_text())


api_blueprint = FlaskApi(
    specification=load_specification(),
    base_path="/code_editor/api",
    options={
        "swagger_ui": conf.getboolean("webserver", "enable_swagger_ui", fallback=True),
    },
).blueprint
