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
from typing import Any, Dict, List, Optional
from airflow_code_editor.utils import (
    git_absolute_path,
    get_plugin_boolean_config,
    execute_git_command,
    mount_points,
    normalize_path,
)

__all__ = ['get_tree']


def get_root_node(path: Optional[str] = None) -> List[Dict[str, Any]]:
    " Get tree root node "
    result = []
    # Mounts
    result.append({'id': 'files', 'label': 'Files', 'leaf': False, 'icon': 'fa-home'})
    for mount in sorted(k for k, v in mount_points.items() if not v.default):
        mount = mount.rstrip('/')
        result.append(
            {
                'id': 'files/~' + mount,
                'label': mount,
                'icon': 'fa-folder',
                'leaf': False,
            }
        )
    # If git is enabled, include the following nodes
    if get_plugin_boolean_config('git_enabled'):
        # Git Workspace
        result.append(
            {
                'id': 'workspace',
                'label': 'Git Workspace',
                'leaf': True,
                'icon': 'fa-briefcase',
            }
        )
        # Tags
        result.append({'id': 'tags', 'label': 'Tags', 'leaf': False, 'icon': 'fa-tags'})
        # Local Branches
        result.append(
            {
                'id': 'local-branches',
                'label': 'Local Branches',
                'leaf': False,
                'icon': 'fa-code-fork',
            }
        )
        # Remote Branches
        result.append(
            {
                'id': 'remote-branches',
                'label': 'Remote Branches',
                'leaf': False,
                'icon': 'fa-globe',
            }
        )
    return result


def get_tags_node(path: Optional[str] = None) -> List[Dict[str, Any]]:
    " Get tree tags node "
    result = []
    r = execute_git_command(['tag'])
    if r.headers.get('X-Git-Return-Code') != '0':
        return result
    for line in r.data.decode('utf-8').split('\n'):
        if line:
            name = line.strip()
            result.append({'id': name, 'leaf': True, 'icon': 'fa-tags'})
    return result


def get_local_branches_node(path: Optional[str] = None) -> List[Dict[str, Any]]:
    " Get tree local branches node "
    result = []
    r = execute_git_command(['branch'])
    if r.headers.get('X-Git-Return-Code') != '0':
        return result
    for line in r.data.decode('utf-8').split('\n'):
        if line:
            name = line.strip()
            if name.startswith('*'):
                name = name[1:].strip()
            result.append({'id': name, 'leaf': True, 'icon': 'fa-code-fork'})
    return result


def get_remote_branches_node(path: Optional[str] = None) -> List[Dict[str, Any]]:
    " Get tree remote branches node "
    result = []
    r = execute_git_command(['branch', '--remotes'])
    if r.headers.get('X-Git-Return-Code') != '0':
        return result
    for line in r.data.decode('utf-8').split('\n'):
        if line:
            name = line.split('->')[0].strip()
            if name.startswith('*'):
                name = name[1:].strip()
            result.append({'id': name, 'leaf': True, 'icon': 'fa-globe'})
    return result


def get_files_node(path: Optional[str] = None) -> List[Dict[str, Any]]:
    " Get tree files node "
    result = []
    dirpath: str = git_absolute_path(path)
    for name in sorted(os.listdir(dirpath)):
        if name.startswith('.') or name == '__pycache__':
            continue
        fullname = os.path.join(dirpath, name)
        leaf = not os.path.isdir(fullname)
        result.append(
            {'id': name, 'leaf': leaf, 'icon': 'fa-file' if leaf else 'fa-folder'}
        )
    return result


TREE_NODES = {
    None: get_root_node,
    'tags': get_tags_node,
    'local-branches': get_local_branches_node,
    'remote-branches': get_remote_branches_node,
    'files': get_files_node,
}


def get_tree(path: Optional[str] = None) -> List[Dict[str, Any]]:
    " Get tree nodes "
    if not path:
        root = None
        path_argv = None
    else:
        splitted_path = path.split('/', 1)
        root = splitted_path.pop(0)
        path_argv = normalize_path(splitted_path.pop(0) if splitted_path else None)
    if root in TREE_NODES:
        return TREE_NODES[root](path_argv)
    else:
        return []
