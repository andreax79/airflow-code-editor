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

import os
import os.path
from typing import cast, List
from flask import jsonify
from airflow import configuration
from airflow_code_editor.commons import (
    PLUGIN_NAME,
    PLUGIN_DEFAULT_CONFIG,
    Path,
)


__all__ = [
    'normalize_path',
    'get_plugin_config',
    'get_plugin_boolean_config',
    'get_plugin_int_config',
    'git_enabled',
    'get_root_folder',
    'error_message',
    'prepare_api_response',
    'always',
]


def normalize_path(path: Path) -> str:
    comps = (path or '/').split('/')
    result: List[str] = []
    for comp in comps:
        if comp in ('', '.'):
            pass
        elif comp != '..' or (result and result[-1] == '..'):
            result.append(comp)
        elif result:
            result.pop()
    return '/'.join(result)


def get_plugin_config(key: str) -> str:
    "Get a plugin configuration/default for a given key"
    return cast(str, configuration.conf.get(PLUGIN_NAME, key, fallback=PLUGIN_DEFAULT_CONFIG[key]))  # type: ignore


def get_plugin_boolean_config(key: str) -> bool:
    "Get a plugin boolean configuration/default for a given key"
    return cast(
        bool,
        configuration.conf.getboolean(
            PLUGIN_NAME, key, fallback=PLUGIN_DEFAULT_CONFIG[key]
        ),
    )  # type: ignore


def get_plugin_int_config(key: str) -> int:
    "Get a plugin int configuration/default for a given key"
    return cast(
        int,
        configuration.conf.getint(
            PLUGIN_NAME, key, fallback=PLUGIN_DEFAULT_CONFIG[key]
        ),
    )  # type: ignore


def git_enabled() -> bool:
    "Return true if git is enabled in the configuration"
    return get_plugin_boolean_config('git_enabled')


def get_root_folder() -> str:
    "Return the configured root folder or Airflow DAGs folder"
    return os.path.abspath(
        get_plugin_config('root_directory')
        or cast(str, configuration.conf.get('core', 'dags_folder'))  # type: ignore
    )


def error_message(ex: Exception) -> str:
    "Get exception error message"
    if ex is None:
        return ''
    elif hasattr(ex, 'strerror'):
        return ex.strerror
    elif hasattr(ex, 'message'):
        return ex.message
    else:
        return str(ex)


def prepare_api_response(error_message=None, **kargs):
    "Prepare API response (JSON)"
    result = dict(kargs)
    if error_message is not None:
        result['error'] = {'message': error_message}
    return jsonify(result)


def always() -> bool:
    "Always return True"
    return True
