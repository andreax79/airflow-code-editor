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

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

__all__ = [
    'PLUGIN_NAME',
    'MENU_CATEGORY',
    'MENU_LABEL',
    'ROUTE',
    'STATIC',
    'CONFIG_SECTION',
    'DEFAULT_GIT_BRANCH',
    'SUPPORTED_GIT_COMMANDS',
    'HTTP_200_OK',
    'HTTP_404_NOT_FOUND',
    'PLUGIN_DEFAULT_CONFIG',
    'ROOT_MOUNTPOUNT',
    'JS_FILES',
    'ICON_HOME',
    'ICON_GIT',
    'ICON_TAGS',
    'FILE_ICON',
    'FOLDER_ICON',
    'ICON_LOCAL_BRANCHES',
    'ICON_REMOTE_BRANCHES',
    'VERSION_FILE',
    'VERSION',
    'Args',
    'GitOutput',
    'TreeOutput',
    'TreeFunc',
]

PLUGIN_NAME = 'code_editor'
MENU_CATEGORY = 'Admin'
MENU_LABEL = 'DAGs Code Editor'
ROUTE = '/' + PLUGIN_NAME
STATIC = '/static/' + PLUGIN_NAME
CONFIG_SECTION = PLUGIN_NAME + '_plugin'
DEFAULT_GIT_BRANCH = 'main'
HTTP_200_OK = 200
HTTP_404_NOT_FOUND = 404
SUPPORTED_GIT_COMMANDS = [
    'add',
    'branch',
    'cat-file',
    'checkout',
    'commit',
    'diff',
    'log',
    'ls-tree',
    'pull',
    'push',
    'reset',
    'rm',
    'show',
    'stage',
    'status',
    'tag',
    'unstage',
]
PLUGIN_DEFAULT_CONFIG = {
    'enabled': True,
    'git_enabled': True,
    'git_cmd': 'git',
    'git_default_args': '-c color.ui=true',
    'git_author_name': None,
    'git_author_email': None,
    'git_init_repo': True,
    'root_directory': None,
    'line_length': 88,
    'string_normalization': False,
    'ignored_entries': '.*,__pycache__',
    'search_context': 2,
}
ROOT_MOUNTPOUNT = 'root'
JS_FILES = [
    'codemirror.js',
    'mode/python/python.js',
    'addon/fold/foldcode.js',
    'addon/fold/foldgutter.js',
    'addon/fold/indent-fold.js',
    'addon/fold/comment-fold.js',
    'addon/mode/loadmode.js',
    'addon/mode/simple.js',
    'addon/mode/overlay.js',
    'addon/dialog/dialog.js',
    'addon/search/searchcursor.js',
    'addon/search/search.js',
    'addon/search/jump-to-line.js',
    'mode/meta.js',
    'vim.js',
    'emacs.js',
    'sublime.js',
    'airflow_code_editor.js',
]

ICON_HOME = 'home'
ICON_GIT = 'work'
ICON_TAGS = 'style'
FILE_ICON = 'file'
FOLDER_ICON = 'folder'
ICON_LOCAL_BRANCHES = 'fork_right'
ICON_REMOTE_BRANCHES = 'public'

VERSION_FILE = Path(__file__).parent / "VERSION"
VERSION = VERSION_FILE.read_text().strip()


Args = Dict[str, str]
GitOutput = Union[None, bytes, str]
TreeOutput = List[Dict[str, Any]]
TreeFunc = Callable[[Optional[str], Args], TreeOutput]
