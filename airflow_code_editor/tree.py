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

import re
from datetime import datetime
from typing import Any, Callable, Dict, List, NamedTuple, Optional

import fs

from airflow_code_editor.commons import (
    FOLDER_ICON,
    ICON_GIT,
    ICON_HOME,
    ICON_LOCAL_BRANCHES,
    ICON_REMOTE_BRANCHES,
    ICON_TAGS,
    Args,
    TreeFunc,
    TreeOutput,
)
from airflow_code_editor.fs import RootFS
from airflow_code_editor.git import execute_git_command, git_enabled
from airflow_code_editor.utils import always, normalize_path, read_mount_points_config

__all__ = ['get_tree', 'get_stat']


class NodeDef(NamedTuple):
    get_children: TreeFunc  # Get node children
    label: Optional[str] = None  # Optional node label
    leaf: bool = True  # is leaf?
    icon: str = ''  # Optional icon
    condition: Callable[[], bool] = always  # Node enabled


TREE_NODES: Dict[Optional[str], NodeDef] = {}


def node(
    id: Optional[str] = None,
    label: Optional[str] = None,
    leaf: bool = True,
    icon: str = '',
    condition: Callable[[], bool] = always,
) -> Callable[[TreeFunc], TreeFunc]:
    "Tree node decorator - register the node into the tree"

    def f(func: TreeFunc) -> TreeFunc:
        TREE_NODES[id] = NodeDef(func, label, leaf, icon, condition)
        return func

    return f


@node(id=None, label='Root', leaf=False)
def get_root_node(path: Optional[str], args: Args) -> TreeOutput:
    "Get tree root node"
    result = []
    for id_, node in TREE_NODES.items():
        # Check condition
        if id_ is None or not node.condition():
            continue
        # Add the node
        result.append({'id': id_, 'label': node.label, 'leaf': node.leaf, 'icon': node.icon})
        # If the node is files, add the mount points
        if id_ == 'files':
            mount_points = read_mount_points_config()
            for mount in sorted(k for k, v in mount_points.items() if not v.default):
                mount = mount.rstrip('/')
                result.append(
                    {
                        'id': 'files/~' + mount,
                        'label': mount,
                        'icon': FOLDER_ICON,
                        'leaf': False,
                    }
                )
    return result


@node(id='files', label='Files', leaf=False, icon=ICON_HOME)
def get_files_node(path: Optional[str], args: Args) -> TreeOutput:
    "Get tree files node"
    result = []
    long_ = args.get('long') == 'true'  # long format
    all_ = args.get('all') == 'true'  # do not ignore entries

    for item in RootFS().path(path).iterdir(show_ignored_entries=all_):
        s = item.stat()
        leaf = not item.is_dir()
        if long_:  # Long format
            size = item.size()
            result.append(
                {
                    'id': item.name,
                    'leaf': leaf,
                    'size': size,
                    'mode': s.st_mode,
                    'mtime': datetime.fromtimestamp(int(s.st_mtime)).isoformat() if s.st_mtime else None,
                }
            )
        else:  # Short format
            result.append({'id': item.name, 'leaf': leaf})
    return result


def git_command_output(*args: str) -> List[str]:
    "Execute a git command and return the output as a list of string"
    r = execute_git_command(list(args))
    # Check exit code
    if r.returncode != 0:
        return []
    # Return stdout lines
    return r.stdout.split('\n')


def prepare_git_output(line: str, icon: str) -> Dict[str, Any]:
    "Prepare a result item for tag/local branches/remote branches"
    name = line.lstrip('* ').split('->')[0]
    return {'id': name, 'leaf': True, 'icon': icon}


def prepare_ls_tree_output(line: str) -> Dict[str, Any]:
    "Prepare a result item for ls-tree"
    mode, type_, hash_, size, name = re.split('[\t ]+', line, 4)
    leaf = type_ != 'tree'
    return {
        'id': hash_,
        'label': name,
        'leaf': leaf,
        'size': int(size) if leaf else None,
        'mode': int(mode, 8),
    }


@node(id='git', label='Git Workspace', icon=ICON_GIT, condition=git_enabled)
def get_git_node(path: Optional[str], args: Args) -> TreeOutput:
    "List the contents of a git tree object"
    output = git_command_output('ls-tree', '-l', path or 'HEAD')
    return [prepare_ls_tree_output(line) for line in output if line]


@node(id='tags', label='Tags', leaf=False, icon=ICON_TAGS, condition=git_enabled)
def get_tags_node(path: Optional[str], args: Args) -> TreeOutput:
    "Get tree tags node"
    if path:
        return get_git_node(path, args)
    output = git_command_output('tag')
    return [prepare_git_output(line, ICON_TAGS) for line in output if line]


@node(
    id='local-branches',
    label='Local Branches',
    leaf=False,
    icon=ICON_LOCAL_BRANCHES,
    condition=git_enabled,
)
def get_local_branches_node(path: Optional[str], args: Args) -> TreeOutput:
    "Get tree local branches node"
    if path:
        return get_git_node(path, args)
    output = git_command_output('branch')
    return [prepare_git_output(line, ICON_LOCAL_BRANCHES) for line in output if line]


@node(
    id='remote-branches',
    label='Remote Branches',
    leaf=False,
    icon=ICON_REMOTE_BRANCHES,
    condition=git_enabled,
)
def get_remote_branches_node(path: Optional[str], args: Args) -> TreeOutput:
    "Get tree remote branches node"
    if path:
        return get_git_node(path, args)
    output = git_command_output('branch', '--remotes')
    return [prepare_git_output(line, ICON_REMOTE_BRANCHES) for line in output if line]


def get_tree(path: Optional[str] = None, args: Args = {}) -> TreeOutput:
    "Get tree nodes at the given path"
    if not path:
        root = None
        path_argv = None
    else:
        splitted_path = path.split('/', 1)
        root = splitted_path.pop(0)
        path_argv = normalize_path(splitted_path.pop(0) if splitted_path else None)
    if root not in TREE_NODES:
        return []
    # Check condition
    if not TREE_NODES[root].condition():
        return []
    # Execute node function
    return TREE_NODES[root].get_children(path_argv, args)


def get_stat(path: Optional[str] = None, args: Args = {}) -> TreeOutput:
    "Get stat for the given path"
    try:
        if not path:
            return {'id': path, 'leaf': False, 'exists': True}
        path = normalize_path(path)
        get_tree(path, args)
        return {'id': path, 'leaf': False, 'exists': True}
    except fs.errors.DirectoryExpected:
        return {'id': path, 'leaf': True, 'exists': True}
    except fs.errors.ResourceNotFound:
        return {'id': path, 'leaf': None, 'exists': False}
