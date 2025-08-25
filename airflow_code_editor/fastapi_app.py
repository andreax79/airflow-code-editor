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

from importlib.resources import files

from airflow.plugins_manager import AirflowPlugin
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from airflow_code_editor.api.fastapi_endpoints import app
from airflow_code_editor.commons import MENU_LABEL, PLUGIN_LONG_NAME, PLUGIN_NAME
from airflow_code_editor.utils import is_enabled

__all__ = ["fastapi_app"]

# ############################################################################
# FastAPI (Airflow 3.x)

# Mount static assets directory
app.mount("/static", StaticFiles(packages=[("airflow_code_editor", "static")]), name="static")

# Prepare templates
templates_path = files("airflow_code_editor").joinpath("templates")
templates = Jinja2Templates(directory=str(templates_path))


# Render the index page
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


fastapi_app = {
    "app": app,
    "url_prefix": f"/{PLUGIN_NAME}",
    "name": PLUGIN_LONG_NAME,
}

menu = {
    "name": MENU_LABEL,
    "href": f"{PLUGIN_NAME}/",
}


# Plugin
class CodeEditorPlugin(AirflowPlugin):
    name = 'editor_plugin'
    fastapi_apps = [fastapi_app] if is_enabled() else []
    appbuilder_menu_items = [menu] if is_enabled() else []
