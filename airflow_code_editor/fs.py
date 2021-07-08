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

import os
import os.path
import shutil
from collections import namedtuple
from typing import Dict, List
import flask
from flask import request
from airflow import configuration
from airflow_code_editor.commons import (
    PLUGIN_NAME,
    ROOT_MOUNTPOUNT,
    Path,
)
from airflow_code_editor.utils import get_root_folder, normalize_path

__all__ = [
    'get_mount_points',
    'isdir',
    'unlink',
    'rmdir',
    'move',
    'listdir',
    'stat',
    'send_file',
    'write_file',
]


MountPoint = namedtuple('MountPoint', 'path default ro')


def read_mount_points_config() -> Dict[str, MountPoint]:
    " Read the mount points configuration "
    config = {
        ROOT_MOUNTPOUNT: MountPoint(path=get_root_folder(), default=True, ro=False)
    }
    i = 0
    # Iterate over the configurations
    while True:
        # the first configuration item doesn't have a suffix
        suffix = str(i) if i != 0 else ''
        try:
            if not configuration.conf.has_option(
                PLUGIN_NAME, 'mount{}_name'.format(suffix)
            ):
                break
        except Exception:  # backports.configparser.NoSectionError and friends
            break
        name = configuration.conf.get(PLUGIN_NAME, 'mount{}_name'.format(suffix))
        path = configuration.conf.get(PLUGIN_NAME, 'mount{}_path'.format(suffix))
        config[name] = MountPoint(path=path, default=False, ro=False)
        i = i + 1
    return config


mount_points = read_mount_points_config()


def get_mount_points(include_default: bool = False) -> Dict[str, MountPoint]:
    " Get mount points "
    if include_default:
        return mount_points
    else:
        return {k: v for k, v in mount_points.items() if not v.default}


def get_absolute_path(git_path: Path) -> str:
    " Git relative path to absolute path "
    path: str = normalize_path(git_path)
    if path.startswith('~'):
        # Expand paths beginning with '~'
        prefix, remain = path.split('/', 1) if '/' in path else (path, '')
        try:
            return os.path.join(mount_points[prefix[1:]].path, remain)
        except KeyError:
            pass
    return os.path.join(get_root_folder(), path)


def isdir(path: Path, **kwargs):
    " Check if *path* is a directory "
    path = get_absolute_path(path)
    return os.path.isdir(path, **kwargs)


def unlink(path: Path, **kwargs):
    " Unix equivalent *unlink* "
    path = get_absolute_path(path)
    return os.unlink(path, **kwargs)


def rmdir(path: Path, recursive=True, **kwargs):
    " Remove the directory *path* "
    path = get_absolute_path(path)
    if recursive:
        return shutil.rmtree(path, **kwargs)
    else:
        return os.rmdir(path, **kwargs)


def move(source: Path, target: Path):
    " Recursively move a file or directory to another location "
    source = get_absolute_path(source)
    target = get_absolute_path(target)
    return shutil.move(source, target)


def listdir(path: Path) -> List[str]:
    " Return a list containing the names of the files in the directory "
    path = get_absolute_path(path)
    try:
        return os.listdir(path)
    except IOError:
        return []


def stat(path: Path):
    " Perform a stat system call on the given path "
    path = get_absolute_path(path)
    return os.stat(path)


def send_file(path: Path, as_attachment: bool = False):
    " Send the contents of a file to the client "
    fullpath = get_absolute_path(path)
    return flask.send_file(fullpath, as_attachment=as_attachment)


def write_file(path: Path, mime_type: str = "text/plain"):
    fullpath = get_absolute_path(path)
    is_text = mime_type.startswith("text/")
    if is_text:
        data = request.get_data(as_text=True)
        # Newline fix (remove cr)
        data = data.replace("\r", "").rstrip()
        os.makedirs(os.path.dirname(fullpath), exist_ok=True)
        with open(fullpath, "w") as f:
            f.write(data)
            f.write("\n")
    else:  # Binary file
        data = request.get_data()
        os.makedirs(os.path.dirname(fullpath), exist_ok=True)
        with open(fullpath, "wb") as f:
            f.write(data)
