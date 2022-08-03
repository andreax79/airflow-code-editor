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
import fs
from fs.mountfs import MountFS, MountError
from fs.multifs import MultiFS
from fs.path import abspath, forcedir, normpath
from typing import Any, List, Union
from flask import abort, send_file, stream_with_context, Response
from airflow_code_editor.utils import read_mount_points_config
from airflow_code_editor.commons import HTTP_404_NOT_FOUND

__all__ = [
    'RootFS',
]

STAT_FIELDS = [
    "st_mode",
    "st_ino",
    "st_dev",
    "st_nlink",
    "st_uid",
    "st_gid",
    "st_size",
    "st_atime",
    "st_mtime",
    "st_ctime",
]

SEND_FILE_CHUNK_SIZE = 8192


def split(pathname: str):
    "Split a pathname, returns tuple (head, tail)"
    pathname = pathname.rstrip("/")
    i = pathname.rfind("/") + 1
    if i == 0:
        return ("/", pathname)
    else:
        return pathname[: i - 1], pathname[i:]


class RootFS(MountFS):
    "Root filesystem with mountpoints"

    def __init__(self):
        super().__init__()
        mounts = read_mount_points_config()
        # Set default fs (root)
        self.default_fs = MultiFS()
        self.tmp_fs = fs.open_fs("mem://")
        self.default_fs.add_fs('tmp', self.tmp_fs, write=False, priority=0)
        self.root_fs = [fs.open_fs(v.path) for v in mounts.values() if v.default][0]
        self.default_fs.add_fs('root', self.root_fs, write=True, priority=1)
        # Mount other fs
        for k, v in mounts.items():
            if not v.default:
                self.mount("/~" + k, fs.open_fs(v.path))

    def mount(self, path, fs_):
        "Mounts a host FS object on a given path"
        if isinstance(fs_, str):
            fs_ = fs.open_fs(fs_)
        path_ = forcedir(abspath(normpath(path)))
        for mount_path, _ in self.mounts:
            if path_.startswith(mount_path):
                raise MountError("mount point overlaps existing mount")
        self.mounts.append((path_, fs_))
        # Create mountpoint on the temporary filesystem
        self.tmp_fs.makedirs(path_, recreate=True)

    def path(self, *parts: List[str]):
        "Return a FSPath instance for the given path"
        return FSPath(*parts, root_fs=self)


class FSPath(object):
    def __init__(self, *parts: List[str], root_fs: RootFS) -> None:
        self.root_fs = root_fs
        self.path = os.path.join("/", *parts)

    def open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
        "Open the file pointed by this path and return a file object"
        return self.root_fs.open(
            self.path,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    @property
    def name(self) -> str:
        "The final path component"
        return split(self.path)[1]

    @property
    def parent(self):
        "The logical parent of the path"
        return self.root_fs.path(split(self.path)[0])

    def touch(self, mode=0o666, exist_ok=True):
        "Create this file"
        return self.root_fs.touch(self.path)

    def rmdir(self) -> None:
        "Remove this directory"
        self.root_fs.removedir(self.path)

    def unlink(self, missing_ok: bool = False) -> None:
        "Remove this file"
        try:
            self.root_fs.remove(self.path)
        except fs.errors.ResourceNotFound:
            if not missing_ok:
                raise FileNotFoundError(self.path)

    def delete(self) -> None:
        "Remove this file or directory"
        if self.is_dir():
            self.rmdir()
        else:
            self.unlink()

    def stat(self):
        "File stat"
        info = self.root_fs.getinfo(self.path, namespaces=["stat"])
        if not info.has_namespace("stat"):
            return os.stat_result([None for _ in STAT_FIELDS])
        return os.stat_result([info.raw["stat"].get(field) for field in STAT_FIELDS])

    def is_dir(self) -> bool:
        "Return True if this path is a directory"
        try:
            return self.root_fs.isdir(self.path)
        except Exception:
            return False

    def resolve(self):
        "Make the path absolute"
        return self.root_fs.path(os.path.realpath(self.path))

    def exists(self):
        "Check if this path exists"
        return self.root_fs.exists(self.path)

    def iterdir(self):
        "Iterate over the files in this directory"
        try:
            for name in sorted(self.root_fs.listdir(self.path)):
                if name.startswith(".") or name == "__pycache__":
                    continue
                yield self.root_fs.path(self.path, name)
        except IOError:
            yield from []

    def size(self) -> int:
        "Return file size for files and number of files for directories"
        if self.is_dir():
            return len(self.root_fs.listdir(self.path))
        else:
            return self.root_fs.getsize(self.path)

    def move(self, target) -> None:
        "Move/rename a file or directory"
        target = self.root_fs.path(target)
        if target.is_dir():
            self.root_fs.move(self.path, (target / self.name).path)
        else:
            self.root_fs.move(self.path, target.path)

    def read_file_chunks(self, chunk_size: int = SEND_FILE_CHUNK_SIZE):
        "Read file in chunks"
        with self.root_fs.openbin(self.path) as f:
            while True:
                buffer = f.read(chunk_size)
                if buffer:
                    yield buffer
                else:
                    break

    def send_file(self, as_attachment: bool):
        "Send the contents of a file to the client"
        if not self.exists():
            abort(HTTP_404_NOT_FOUND)
        elif self.root_fs.hassyspath(self.path):
            # Local filesystem
            return send_file(
                self.root_fs.getsyspath(self.path),
                as_attachment=as_attachment,
                attachment_filename=self.name if as_attachment else None,
            )
        else:
            # Other filesystems
            response = Response(stream_with_context(self.read_file_chunks()))
            if as_attachment:
                response.headers[
                    'Content-Disposition'
                ] = 'attachment;filename={}'.format(self.name)
            return response

    def write_file(self, data: Union[str, bytes], is_text: bool) -> None:
        "Write data to a file"
        self.root_fs.makedirs(self.parent.path, recreate=True)
        if is_text:
            self.root_fs.writetext(self.path, data)
        else:
            self.root_fs.writebytes(self.path, data)

    def read_text(self, encoding=None, errors=None) -> str:
        "Get the contents of a file as a string"
        return self.root_fs.readtext(self.path, encoding=encoding, errors=errors)

    def read_bytes(self) -> bytes:
        "Get the contents of a file as bytes"
        return self.root_fs.readbytes(self.path)

    def __str__(self) -> str:
        return self.path

    def __truediv__(self, key):
        try:
            path = os.path.join(self.path, key)
            return self.root_fs.path(path)
        except TypeError:
            return NotImplemented

    def __eq__(self, other) -> bool:
        if not isinstance(other, FSPath):
            return NotImplemented
        return self.path == other.path

    def __hash__(self) -> int:
        try:
            return self._hash
        except AttributeError:
            self._hash = hash(self.path)
            return self._hash

    def __lt__(self, other: Any):
        if not isinstance(other, FSPath):
            return NotImplemented
        return self.path < other.path

    def __le__(self, other: Any) -> bool:
        if not isinstance(other, FSPath):
            return NotImplemented
        return self.path <= other.path

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, FSPath):
            return NotImplemented
        return self.path > other.path

    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, FSPath):
            return NotImplemented
        return self.path >= other.path