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

from importlib.resources import files
from pathlib import Path

import platformdirs
import starlette.status as status
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from airflow_code_editor.api.fastapi_endpoints import app as code_editor_app
from airflow_code_editor.commons import ROUTE
from airflow_code_editor.utils import read_config_file

__all__ = ["app"]

CONFIG_DIR = Path(platformdirs.user_config_dir(appname="CodeEditor"))
CONFIG_PATH = CONFIG_DIR / "config.ini"

# Read the configuration
read_config_file(CONFIG_PATH)

# Mount static assets directory
code_editor_app.mount("/static", StaticFiles(packages=[("airflow_code_editor", "static")]), name="static")

# Prepare templates
templates_path = files("airflow_code_editor").joinpath("templates")
templates = Jinja2Templates(directory=str(templates_path))


# Render the index page
@code_editor_app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Mount the app
app = FastAPI()
app.mount(ROUTE, code_editor_app)


# Redirect root to /code_editor
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return RedirectResponse(url=ROUTE, status_code=status.HTTP_302_FOUND)
