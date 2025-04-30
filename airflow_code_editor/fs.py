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

import errno
import os
from fnmatch import fnmatch
from typing import Any, List, Optional, Tuple, Union

import fs
from fs.mountfs import MountError, MountFS
from fs.multifs import MultiFS
from fs.path import abspath, forcedir, normpath
from fs.walk import Walker
from psslib.contentmatcher import ContentMatcher
from psslib.driver import LINE_CONTEXT, LINE_MATCH, _build_match_context_dict
from psslib.utils import istextfile

from airflow_code_editor.utils import (
    get_plugin_config,
    get_plugin_int_config,
    read_mount_points_config,
    send_file,
)

__all__ = [
    "RootFS",
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
        self.default_fs.add_fs("tmp", self.tmp_fs, write=False, priority=0)
        self.root_fs = [fs.open_fs(v.path) for v in mounts.values() if v.default][0]
        self.default_fs.add_fs("root", self.root_fs, write=True, priority=1)
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

    def find_files(
        self,
        path: str = "/",
        filter: Union[List[str], str, None] = None,
        exclude: Optional[List[str]] = None,
        max_depth: Optional[int] = None,
    ):
        "Walk a filesystem, yielding FSPAth"
        if exclude == []:
            exclude = None
        if isinstance(filter, str):
            filter = [filter]
        walker = Walker(
            ignore_errors=True,
            filter=filter,
            exclude=exclude,
            exclude_dirs=exclude,
            max_depth=max_depth,
        )
        fs = self.root_fs
        for filename in walker.files(fs=fs, path=path):
            yield self.path(filename)

    def search(
        self,
        query: str,
        search_context: Optional[int] = None,
        path: str = "/",
        filter: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        max_depth: Optional[int] = None,
    ):
        "Search for pattern in files"
        if search_context is None:
            search_context = get_plugin_int_config("search_context")
        if exclude is None:
            exclude = get_plugin_config("ignored_entries").split(",")

        result = []
        matcher = ContentMatcher(pattern=query.encode("utf-8"))
        for path in self.find_files(filter=filter, exclude=exclude, max_depth=max_depth):
            try:
                with path.open("rb") as f:
                    if istextfile(f):
                        f.seek(0)
                        matches = list(matcher.match_file(f))
                        if not search_context:
                            for match in matches:
                                context = match[0].decode("utf-8")
                                row_number = match[1]
                                result.append(
                                    {
                                        "row_number": row_number,  # matching row number
                                        "context_first_row": row_number,  # context first row number
                                        "context": context,  # context (matching row)
                                        "path": path.path,  # file path
                                    }
                                )
                        else:
                            for row, context, context_first_row in prepare_search_context(f, matches, search_context):
                                result.append(
                                    {
                                        "row_number": row,  # matching row number
                                        "context_first_row": context_first_row,  # context first row number
                                        "context": context,  # context
                                        "path": path.path,  # file path
                                    }
                                )
            except (OSError, IOError):
                pass

        return result


def prepare_search_context(f, matches, search_context) -> Tuple[int, str, int]:
    f.seek(0)
    match_context_dict = _build_match_context_dict(matches, search_context, search_context)
    lines = []
    context_first_row = 0
    row_number = 0

    prev_was_blank = False
    had_context = False
    for current_row_number, current_line in enumerate(f, 1):
        current_line = current_line.decode("utf-8")
        result, match = match_context_dict.get(current_row_number, (None, None))
        if result is None:
            prev_was_blank = True
            continue

        elif result == LINE_MATCH:
            row_number = current_row_number
            if current_row_number < context_first_row or context_first_row == 0:
                context_first_row = current_row_number
            lines.append(current_line)

        elif result == LINE_CONTEXT:
            if prev_was_blank and had_context:
                context = "".join(lines)
                yield row_number, context, context_first_row
                lines = []
                context_first_row = current_row_number
            if context_first_row < context_first_row or context_first_row == 0:
                context_first_row = current_row_number
            lines.append(current_line)
            had_context = True
        prev_was_blank = False

    if lines:
        context = "".join(lines)
        yield row_number, context, context_first_row


class FSPath(object):
    def __init__(self, *parts: List[str], root_fs: RootFS) -> None:
        self.root_fs = root_fs
        self.path = os.path.join("/", *parts)

    def open(self, mode="r", buffering=-1, encoding=None, errors=None, newline=None):
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

    def iterdir(self, show_ignored_entries=False):
        "Iterate over the files in this directory"
        ignored_entries = get_plugin_config("ignored_entries").split(",")
        mount_points = [x[0].rstrip("/") for x in self.root_fs.mounts]
        for name in sorted(self.root_fs.listdir(self.path)):
            skip = False
            if not show_ignored_entries:
                fullpath = os.path.join(self.path, name)
                # Skip mount points
                if fullpath in mount_points:
                    skip = True
                # Ship hidden files
                for pattern in ignored_entries:
                    if fnmatch(fullpath if pattern.startswith("/") else name, pattern.strip()):
                        skip = True
            if not skip:
                yield self.root_fs.path(self.path, name)

    def size(self) -> Optional[int]:
        "Return file size for files and number of files for directories"
        try:
            if self.is_dir():
                return len(self.root_fs.listdir(self.path))
            else:
                return self.root_fs.getsize(self.path)
        except fs.errors.FSError:
            return None

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
            raise FileNotFoundError(errno.ENOENT, "File not found", self.path)
        elif self.root_fs.hassyspath(self.path):
            # Local filesystem
            if as_attachment:
                # Send file as attachment (set Content-Disposition: attachment header)
                return send_file(
                    self.root_fs.getsyspath(self.path),
                    as_attachment=True,
                    download_name=self.name,
                )
            else:
                return send_file(self.root_fs.getsyspath(self.path))
        else:
            # Other filesystems
            return send_file(
                self.read_file_chunks(),
                as_attachment=as_attachment,
                download_name=self.name,
                stream=True,
            )

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

    def __repr__(self) -> str:
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
