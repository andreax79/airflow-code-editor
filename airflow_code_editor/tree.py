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
import re
import stat
from datetime import datetime
from typing import Any, Callable, Dict, List, NamedTuple, Optional
from airflow_code_editor.commons import (
    Args,
    Path,
    TreeFunc,
    TreeOutput,
)
from airflow_code_editor.utils import (
    always,
    git_absolute_path,
    git_enabled,
    execute_git_command,
    mount_points,
    normalize_path,
)

__all__ = ['get_tree']


class NodeDef(NamedTuple):
    get_children: TreeFunc  # Get node children
    label: Optional[str] = None  # Optional node label
    leaf: bool = True  # is leaf?
    icon: str = ''  # Optiona icon
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
def get_root_node(path: Path, args: Args) -> TreeOutput:
    "Get tree root node"
    result = []
    for id_, node in TREE_NODES.items():
        # Check condition
        if id_ is None or not node.condition():
            continue
        # Add the node
        result.append(
            {'id': id_, 'label': node.label, 'leaf': node.leaf, 'icon': node.icon}
        )
        # If the node is files, add the mount points
        if id_ == 'files':
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
    return result


@node(id='files', label='Files', leaf=False, icon='fa-home')
def get_files_node(path: Path, args: Args) -> TreeOutput:
    "Get tree files node"

    def try_listdir(path: str) -> List[str]:
        try:
            return os.listdir(path)
        except IOError:
            return []

    result = []
    dirpath: str = git_absolute_path(path)
    long_ = 'long' in args
    for name in sorted(try_listdir(dirpath)):
        if name.startswith('.') or name == '__pycache__':
            continue
        fullname = os.path.join(dirpath, name)
        s = os.stat(fullname)
        leaf = not stat.S_ISDIR(s.st_mode)
        if long_:  # Long format
            size = s.st_size if leaf else len(try_listdir(fullname))
            result.append(
                {
                    'id': name,
                    'leaf': leaf,
                    'size': size,
                    'mode': s.st_mode,
                    'mtime': datetime.fromtimestamp(int(s.st_mtime)).isoformat()
                }
            )
        else:  # Short format
            result.append(
                {
                    'id': name,
                    'leaf': leaf
                }
            )
    return result


def git_command_output(*args: str) -> List[str]:
    "Execute a git command and return the output as a list of string"
    r = execute_git_command(list(args))
    # Check exit code
    if r.headers.get('X-Git-Return-Code') != '0':
        return []
    # Return stdout lines
    return r.data.decode('utf-8').split('\n')


def prepare_git_output(line: str, icon: str) -> Dict[str, Any]:
    "Prepate a result item for tag/local branches/remote branches"
    name = line.lstrip('* ').split('->')[0]
    return {'id': name, 'leaf': True, 'icon': icon}


def prepare_ls_tree_output(line: str) -> Dict[str, Any]:
    "Prepate a result item for ls-tre"
    mode, type_, hash_, size, name = re.split('[\t ]+', line, 4)
    leaf = type_ != 'tree'
    return {
        'id': hash_,
        'label': name,
        'leaf': leaf,
        'size': int(size) if leaf else None,
        'mode': int(mode, 8)
    }


@node(id='git', label='Git Workspace', icon='fa-briefcase', condition=git_enabled)
def get_git_node(path: Path, args: Args) -> TreeOutput:
    "List the contents of a git tree object"
    output = git_command_output('ls-tree', '-l', path or 'HEAD')
    return [prepare_ls_tree_output(line) for line in output if line]


@node(id='tags', label='Tags', leaf=False, icon='fa-tags', condition=git_enabled)
def get_tags_node(path: Path, args: Args) -> TreeOutput:
    "Get tree tags node"
    if path:
        return get_git_node(path, args)
    output = git_command_output('tag')
    return [prepare_git_output(line, 'fa-tags') for line in output if line]


@node(
    id='local-branches',
    label='Local Branches',
    leaf=False,
    icon='fa-code-fork',
    condition=git_enabled,
)
def get_local_branches_node(path: Path, args: Args) -> TreeOutput:
    "Get tree local branches node"
    if path:
        return get_git_node(path, args)
    output = git_command_output('branch')
    return [prepare_git_output(line, 'fa-code-fork') for line in output if line]


@node(
    id='remote-branches',
    label='Remote Branches',
    leaf=False,
    icon='fa-globe',
    condition=git_enabled,
)
def get_remote_branches_node(path: Path, args: Args) -> TreeOutput:
    "Get tree remote branches node"
    if path:
        return get_git_node(path, args)
    output = git_command_output('branch', '--remotes')
    return [prepare_git_output(line, 'fa-globe') for line in output if line]


def get_tree(path: Path = None, args: Args = {}) -> TreeOutput:
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
