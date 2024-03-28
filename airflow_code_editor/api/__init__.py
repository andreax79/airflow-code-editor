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

import importlib.resources

from airflow.configuration import conf
from airflow.utils.yaml import safe_load
from connexion import FlaskApi

__all__ = ["api_blueprint"]


def load_specification() -> dict:
    with importlib.resources.path("airflow_code_editor.api", "code_editor.yaml") as f:
        return safe_load(f.read_text())


api_blueprint = FlaskApi(
    specification=load_specification(),
    base_path="/code_editor/api",
    options={
        "swagger_ui": conf.getboolean("webserver", "enable_swagger_ui", fallback=True),
        #     "swagger_path": os.fspath(ROOT_APP_DIR.joinpath("www", "static", "dist", "swagger-ui")),
    },
).blueprint
