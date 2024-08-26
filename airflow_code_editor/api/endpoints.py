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

from airflow.api_connexion import security
from airflow.www.app import csrf
from flask import request

from airflow_code_editor.code_editor_view import AbstractCodeEditorView


@security.requires_access_dag("GET")
@csrf.exempt
def get_tree(*, path: str = None):
    "List tree entries"
    return AbstractCodeEditorView._tree(path, args=request.args, method="GET")


@security.requires_access_dag("GET")
@csrf.exempt
def get_tree_root():
    "List root tree entries"
    return AbstractCodeEditorView._tree(None, args=request.args, method="GET")


@security.requires_access_dag("GET")
@csrf.exempt
def get_files(*, path: str = None):
    "Get file content"
    return AbstractCodeEditorView._load(path)


@security.requires_access_dag("PUT")
@csrf.exempt
def post_files(*, path: str = None):
    "Write file content"
    return AbstractCodeEditorView._save(path)


@security.requires_access_dag("PUT")
@csrf.exempt
def delete_files(*, path: str = None):
    "Delete a file"
    return AbstractCodeEditorView._delete(path)


@security.requires_access_dag("GET")
@csrf.exempt
def search(*, query: str):
    "File search"
    return AbstractCodeEditorView._search(args=request.args)


@security.requires_access_dag("PUT")
@csrf.exempt
def post_git():
    "Execute a GIT command"
    return AbstractCodeEditorView._execute_git_command()


@security.requires_access_dag("GET")
@csrf.exempt
def get_version():
    "Get version information"
    return AbstractCodeEditorView._get_version()
