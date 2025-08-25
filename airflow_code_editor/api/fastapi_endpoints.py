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

from airflow.api_fastapi.core_api.openapi.exceptions import (
    create_openapi_http_exception_doc,
)
from airflow.api_fastapi.core_api.security import requires_access_dag
from fastapi import Depends, FastAPI, Request, status

from airflow_code_editor.api import api

__all__ = ["app"]

app = FastAPI()


@app.post(
    "/repo",
    dependencies=[Depends(requires_access_dag(method="GET"))],
    include_in_schema=False,
)
async def repo_base(request: Request):
    body = await request.json()
    git_args = body.get("args", [])
    return api.execute_git_command(git_args)


@app.post(
    "/files/{path:path}",
    dependencies=[Depends(requires_access_dag(method="GET"))],
    include_in_schema=False,
)
async def save(path: str, request: Request):
    "Save a file"
    mime_type = request.headers.get("content-type", "text/plain")
    data = await request.body()
    return api.save(path=path, data=data, mime_type=mime_type)


@app.get(
    "/files/{path:path}",
    dependencies=[Depends(requires_access_dag(method="GET"))],
    include_in_schema=False,
)
def load(path: str, request: Request):
    "Send the contents of a file to the client"
    return api.load(path)


@app.delete(
    "/files/{path:path}",
    dependencies=[Depends(requires_access_dag(method="GET"))],
    include_in_schema=False,
)
def delete(path: str, request: Request):
    "Delete a file"
    return api.delete(path)


@app.post(
    "/generate_presigned",
    dependencies=[Depends(requires_access_dag(method="GET"))],
    include_in_schema=False,
)
async def generate_presigned(request: Request):
    "Generate a presigned URL token for downloading a file/git object"
    body = await request.json()
    path = body.get("path", "")
    return api.generate_presigned(path)


@app.get(
    "/presigned/{token}",
    dependencies=[],  # presigned URL does not require authentication
    include_in_schema=False,
)
def presigned(token: str, request: Request):
    "Download a file/git object using a presigned URL"
    return api.load_presigned(token)


@app.post(
    "/format",
    dependencies=[Depends(requires_access_dag(method="GET"))],
    include_in_schema=False,
)
async def format(request: Request):
    "Sort imports and format code"
    data = (await request.body()).decode("utf-8")
    return api.format(data)


@app.get(
    "/tree",
    dependencies=[Depends(requires_access_dag(method="GET"))],
    include_in_schema=False,
)
@app.head(
    "/tree",
    dependencies=[Depends(requires_access_dag(method="GET"))],
    include_in_schema=False,
)
def tree_base(request: Request):
    "Get root tree entries"
    return api.tree(path=None, args=request.query_params, method=request.method)


@app.get(
    "/tree/{path:path}",
    dependencies=[Depends(requires_access_dag(method="GET"))],
    include_in_schema=False,
)
@app.head(
    "/tree/{path:path}",
    dependencies=[Depends(requires_access_dag(method="GET"))],
    include_in_schema=False,
)
def tree(path: str, request: Request):
    "Get tree entries"
    return api.tree(path, args=request.query_params, method=request.method)


@app.get(
    "/search",
    dependencies=[Depends(requires_access_dag(method="GET"))],
    include_in_schema=False,
)
def search(request: Request):
    "File search"
    return api.search(args=request.query_params)


@app.get(
    "/ping",
    dependencies=[Depends(requires_access_dag(method="GET"))],
    include_in_schema=False,
)
def ping():
    "Ping"
    return api.ping()


@app.get(
    "/version",
    dependencies=[Depends(requires_access_dag(method="GET"))],
    include_in_schema=False,
)
def get_version():
    "Get version information"
    return api.get_version()


# ############################################################################
# Public API


@app.get(
    "/api/files/{path:path}",
    responses=create_openapi_http_exception_doc(
        [
            status.HTTP_404_NOT_FOUND,  # File not found
        ]
    ),
    dependencies=[Depends(requires_access_dag(method="GET"))],
)
def api_get_files(path: str, request: Request):
    "Get file content"
    return api.load(path)


@app.post(
    "/api/files/{path:path}",
    responses=create_openapi_http_exception_doc(
        [
            status.HTTP_400_BAD_REQUEST,  # Error writing file
        ]
    ),
    dependencies=[Depends(requires_access_dag(method="GET"))],
)
async def api_post_files(path: str, request: Request):
    "Write file content"
    mime_type = request.headers.get("content-type", "text/plain")
    data = await request.body()
    return api.save(path=path, data=data, mime_type=mime_type)


@app.delete(
    "/api/files/{path:path}",
    responses=create_openapi_http_exception_doc(
        [
            status.HTTP_400_BAD_REQUEST,  # Error deleting file
            status.HTTP_404_NOT_FOUND,  # File not found
        ]
    ),
    dependencies=[Depends(requires_access_dag(method="GET"))],
)
def api_delete_files(path: str, request: Request):
    "Delete a file"
    return api.delete(path)


@app.get(
    "/api/tree",
    dependencies=[Depends(requires_access_dag(method="GET"))],
)
def api_get_tree(request: Request):
    "List root tree entries"
    return api.tree(path=None, args=request.query_params, method=request.method)


@app.get(
    "/api/tree/{path:path}",
    dependencies=[Depends(requires_access_dag(method="GET"))],
)
def api_get_tree_path(path: str, request: Request):
    "Get tree entries"
    return api.tree(path, args=request.query_params, method=request.method)


@app.get(
    "/api/search",
    dependencies=[Depends(requires_access_dag(method="GET"))],
)
def api_get_search(request: Request):
    "Search files"
    return api.search(args=request.query_params)


@app.post(
    "/api/git",
    dependencies=[Depends(requires_access_dag(method="GET"))],
)
async def api_post_git(request: Request):
    "Execute a GIT command"
    body = await request.json()
    git_args = body.get("args", [])
    return api.execute_git_command(git_args)


@app.get(
    "/api/version",
    dependencies=[Depends(requires_access_dag(method="GET"))],
)
def api_get_version():
    "Get version information"
    return api.get_version()
