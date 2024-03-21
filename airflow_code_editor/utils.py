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

import itertools
import json
from collections import namedtuple
from pathlib import Path
from typing import Dict, List, Optional, cast

from airflow import configuration
from flask import Response
from fs.errors import FSError
from pygments.lexer import RegexLexer
from pygments.token import Text

from airflow_code_editor.commons import (
    HTTP_200_OK,
    PLUGIN_DEFAULT_CONFIG,
    PLUGIN_NAME,
    ROOT_MOUNTPOUNT,
)

__all__ = [
    'DummyLexer',
    'always',
    'error_message',
    'get_plugin_boolean_config',
    'get_plugin_config',
    'get_plugin_int_config',
    'get_root_folder',
    'is_enabled',
    'normalize_path',
    'prepare_api_response',
]


# Create a new section in the configuration.
try:
    configuration.conf.add_section(PLUGIN_NAME)
except Exception:
    pass


def normalize_path(path: Optional[str]) -> str:
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
        configuration.conf.getboolean(PLUGIN_NAME, key, fallback=PLUGIN_DEFAULT_CONFIG[key]),
    )  # type: ignore


def get_plugin_int_config(key: str) -> int:
    "Get a plugin int configuration/default for a given key"
    return cast(
        int,
        configuration.conf.getint(PLUGIN_NAME, key, fallback=PLUGIN_DEFAULT_CONFIG[key]),
    )  # type: ignore


def is_enabled() -> bool:
    "Return true if the plugin is enabled in the configuration"
    return get_plugin_boolean_config('enabled')


def get_root_folder() -> Path:
    "Return the configured root folder or Airflow DAGs folder"
    return Path(
        get_plugin_config('root_directory') or cast(str, configuration.conf.get('core', 'dags_folder'))  # type: ignore
    ).resolve()


MountPoint = namedtuple('MountPoint', 'path default')


def read_mount_points_config() -> Dict[str, MountPoint]:
    "Return the plugin configuration"
    path = str(get_root_folder())
    config = {ROOT_MOUNTPOUNT: MountPoint(path=path, default=True)}

    # Iterate over the configurations
    for i in itertools.count():
        # the first configuration doesn't have a suffix
        if i == 0:
            suffix = ''
        else:
            suffix = str(i)
        try:
            if not configuration.conf.has_option(PLUGIN_NAME, 'mount{}'.format(suffix)):
                break
            conf = configuration.conf.get(PLUGIN_NAME, 'mount{}'.format(suffix))
            if conf is None:
                break
        except Exception:
            break
        try:
            mount_conf = {}
            for part in conf.split(','):
                k, v = part.split('=')
                mount_conf[k] = v
            config[mount_conf['name']] = MountPoint(
                path=mount_conf['path'], default=mount_conf['name'] == ROOT_MOUNTPOUNT
            )
        except Exception:
            pass

    # Old configuration format
    for i in itertools.count():
        # the first configuration doesn't have a suffix
        if i == 0:
            suffix = ''
        else:
            suffix = str(i)
        try:
            if not configuration.conf.has_option(PLUGIN_NAME, 'mount{}_name'.format(suffix)):
                break
        except Exception:  # backports.configparser.NoSectionError and friends
            break
        name = configuration.conf.get(PLUGIN_NAME, 'mount{}_name'.format(suffix))
        path = configuration.conf.get(PLUGIN_NAME, 'mount{}_path'.format(suffix))
        config[name] = MountPoint(path=path, default=mount_conf['name'] == ROOT_MOUNTPOUNT)
    return config


def error_message(ex: Exception) -> str:
    "Get exception error message"
    if ex is None:
        return ''
    elif isinstance(ex, FSError):
        return str(ex)
    elif hasattr(ex, 'strerror'):
        return ex.strerror
    elif hasattr(ex, 'message'):
        return ex.message
    else:
        return str(ex)


def prepare_api_response(
    error_message: Optional[str] = None,
    http_status_code: int = HTTP_200_OK,
    **kargs,
) -> Response:
    "Prepare API response (JSON)"
    data = dict(kargs)
    if error_message is not None:
        data['error'] = {'message': error_message}
    return Response(
        response=json.dumps(data),
        mimetype="application/json",
        status=http_status_code,
    )


def always() -> bool:
    "Always return True"
    return True


class DummyLexer(RegexLexer):
    name = "Dummy"
    aliases = ["dummy"]
    filenames = []
    mimetypes = []
    tokens = {
        'root': [
            (r'.*\n', Text),
        ]
    }
