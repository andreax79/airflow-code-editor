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
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import PurePosixPath
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

import fsspec
import fsspec.implementations.local
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
    "FSError",
]


# Custom exceptions to replace fs.errors
class FSError(Exception):
    "Base filesystem error"

    pass


class MountError(FSError):
    "Mount error"

    pass


SEND_FILE_CHUNK_SIZE = 8192


def split(pathname: str):
    "Split a pathname, returns tuple (head, tail)"
    pathname = pathname.rstrip("/")
    i = pathname.rfind("/") + 1
    if i == 0:
        return ("/", pathname)
    else:
        return pathname[: i - 1], pathname[i:]


def normpath(path: str) -> str:
    "Normalize a path"
    return str(PurePosixPath(path))


def abspath(path: str) -> str:
    "Make path absolute"
    if not path.startswith('/'):
        path = '/' + path
    return normpath(path)


def forcedir(path: str) -> str:
    "Ensure path ends with /"
    if not path.endswith('/'):
        return path + '/'
    return path


class RootFS:
    "Root filesystem with mountpoints"

    def __init__(self):
        mounts = read_mount_points_config()
        # Setup filesystems
        self.mounts: List[Tuple[str, fsspec.AbstractFileSystem, str]] = []  # (mount_path, filesystem, base_path)
        # Set default fs (root)
        root_fs_path = [v.path for v in mounts.values() if v.default][0]
        self.root_fs, self.root_fs_base_path = self._open_fs(root_fs_path)
        self.default_fs = self.root_fs
        # Mount other fs
        for k, v in mounts.items():
            if not v.default:
                mount_path = "/~" + k
                self.mount(mount_path, v.path)

    def _open_fs(self, path: str) -> Tuple[fsspec.AbstractFileSystem, str]:
        "Open a filesystem from a path/URL"
        if path.startswith("mem://"):
            return fsspec.filesystem("memory"), "/"
        elif "://" in path:
            # URL-like path, let fsspec handle it
            return fsspec.url_to_fs(path)
        else:
            # Local file path
            return fsspec.filesystem("file"), path

    def _get_fs_and_path(self, path: str) -> Tuple[fsspec.AbstractFileSystem, str]:
        "Get the appropriate filesystem and adjusted path for a given path"
        path = abspath(normpath(path))

        # Check mounts (longest prefix match)
        for mount_path, mount_fs, base_path in sorted(self.mounts, key=lambda x: len(x[0]), reverse=True):
            if path.startswith(mount_path):
                # Calculate relative path from mount point
                rel_path = path[len(mount_path) :].lstrip('/')
                if not rel_path:
                    rel_path = ""
                # Combine base path with relative path
                if base_path:
                    full_path = os.path.join(base_path, rel_path) if rel_path else base_path
                else:
                    full_path = rel_path if rel_path else "/"
                return mount_fs, full_path

        # Use default fs
        if self.root_fs_base_path:
            # For local filesystem, combine with base path
            path = os.path.join(self.root_fs_base_path, path.lstrip('/'))
        return self.default_fs, path

    def mount(self, path: str, fs_or_path: Union[str, fsspec.AbstractFileSystem]) -> None:
        "Mounts a filesystem on a given path"
        if isinstance(fs_or_path, str):
            fs_, base_path = self._open_fs(fs_or_path)
        else:
            fs_ = fs_or_path
            base_path = None

        path = forcedir(abspath(normpath(path)))

        # Check for overlapping mounts
        for mount_path, _, _ in self.mounts:
            if path.startswith(mount_path) or mount_path.startswith(path):
                raise MountError("mount point overlaps existing mount")

        self.mounts.append((path.rstrip('/'), fs_, base_path))

    def path(self, *parts: str):
        "Return a FSPath instance for the given path"
        return FSPath(*parts, root_fs=self)

    def open(self, path: str, mode="r", buffering=-1, encoding=None, errors=None, newline=None):
        "Open a file"
        fs, path = self._get_fs_and_path(path)
        if 'b' in mode:
            # Binary mode
            return fs.open(path, mode=mode)
        else:
            # Text mode
            return fs.open(path, mode=mode, encoding=encoding, errors=errors)

    def exists(self, path: str) -> bool:
        "Check if path exists"
        fs, path = self._get_fs_and_path(path)
        try:
            return fs.exists(path)
        except Exception:
            return False

    def isdir(self, path: str) -> bool:
        "Check if path is a directory"
        fs, path = self._get_fs_and_path(path)
        try:
            return fs.isdir(path)
        except Exception:
            return False

    def isfile(self, path: str) -> bool:
        "Check if path is a file"
        fs, path = self._get_fs_and_path(path)
        try:
            return fs.isfile(path)
        except Exception:
            return False

    def listdir(self, path: str = "/") -> List[str]:
        "List directory contents"
        fs, path = self._get_fs_and_path(path)
        try:
            items = fs.ls(path, detail=False)
            # Extract just the names (basenames)
            result = []
            for item in items:
                # Get basename - handle both regular paths and URLs
                basename = os.path.basename(item.rstrip('/'))
                if basename:  # Skip empty strings
                    result.append(basename)
            return sorted(result)
        except (FileNotFoundError, NotADirectoryError):
            raise FileNotFoundError(path)

    def makedirs(self, path: str, recreate=False, exist_ok=False) -> None:
        "Create directories"
        fs, path = self._get_fs_and_path(path)
        try:
            fs.makedirs(path, exist_ok=recreate or exist_ok)
        except FileExistsError:
            if not (recreate or exist_ok):
                raise

    def remove(self, path: str) -> None:
        "Remove a file"
        fs, path = self._get_fs_and_path(path)
        fs.rm(path, recursive=False)

    def rmdir(self, path: str) -> None:
        "Remove a directory"
        fs, path = self._get_fs_and_path(path)
        fs.rmdir(path)

    def info(self, path: str) -> Dict[str, Union[int, float]]:
        "Get file info"
        fs, path = self._get_fs_and_path(path)
        return fs.info(path)

    def size(self, path: str) -> int:
        "Get file size"
        fs, path = self._get_fs_and_path(path)
        return fs.size(path)

    def move(self, src: str, dst: str) -> None:
        "Move/rename a file or directory"
        src_fs, src_path = self._get_fs_and_path(src)
        dst_fs, dst_path = self._get_fs_and_path(dst)

        if src_fs is dst_fs:
            src_fs.mv(src_path, dst_path, recursive=True)
        else:
            # Cross-filesystem move
            if src_fs.isdir(src_path):
                raise FSError("Cross-filesystem directory moves not supported")
            # Copy then delete
            with src_fs.open(src_path, 'rb') as src_file:
                with dst_fs.open(dst_path, 'wb') as dst_file:
                    dst_file.write(src_file.read())
            src_fs.rm(src_path)

    def copy(self, src: str, dst: str) -> None:
        "Copy a file"
        src_fs, src_path = self._get_fs_and_path(src)
        dst_fs, dst_path = self._get_fs_and_path(dst)

        with src_fs.open(src_path, 'rb') as src_file:
            with dst_fs.open(dst_path, 'wb') as dst_file:
                dst_file.write(src_file.read())

    def read_text(self, path: str, encoding=None, errors=None) -> str:
        "Read text from a file"
        fs, path = self._get_fs_and_path(path)
        with fs.open(path, 'r', encoding=encoding, errors=errors) as f:
            return f.read()

    def read_bytes(self, path: str) -> bytes:
        "Read bytes from a file"
        fs, path = self._get_fs_and_path(path)
        with fs.open(path, 'rb') as f:
            return f.read()

    def write_text(self, path: str, data: str, encoding=None, errors=None):
        "Write text to a file"
        # Ensure parent directory exists
        parent_path = os.path.dirname(path)
        if parent_path and parent_path != '/':
            self.makedirs(parent_path, exist_ok=True)

        fs, path = self._get_fs_and_path(path)
        with fs.open(path, 'w', encoding=encoding, errors=errors) as f:
            f.write(data)

    def write_bytes(self, path: str, data: bytes) -> None:
        "Write bytes to a file"
        # Ensure parent directory exists
        parent_path = os.path.dirname(path)
        if parent_path and parent_path != '/':
            self.makedirs(parent_path, exist_ok=True)

        fs, path = self._get_fs_and_path(path)
        with fs.open(path, 'wb') as f:
            f.write(data)

    def touch(self, path: str) -> None:
        "Create or update a file"
        fs, path = self._get_fs_and_path(path)
        fs.touch(path)

    def get_local_path(self, path: str) -> str:
        "Get local path"
        fs, path = self._get_fs_and_path(path)
        if isinstance(fs, fsspec.implementations.local.LocalFileSystem):
            return path
        else:
            return None

    def find_files(
        self,
        path: str = "/",
        filter: Union[List[str], str, None] = None,
        exclude: Optional[List[str]] = None,
        max_depth: Optional[int] = None,
    ) -> Generator["FSPath", None, None]:
        "Walk a filesystem, yielding FSPath"
        if exclude == []:
            exclude = None
        if isinstance(filter, str):
            filter = [filter]

        def should_exclude(name: str, patterns: Optional[List[str]]) -> bool:
            "Check if name matches any exclude pattern"
            if not patterns:
                return False
            for pattern in patterns:
                if fnmatch(name, pattern):
                    return True
            return False

        def matches_filter(name: str, patterns: Optional[List[str]]) -> bool:
            "Check if name matches any filter pattern"
            if not patterns:
                return True
            for pattern in patterns:
                if fnmatch(name, pattern):
                    return True
            return False

        def walk_recursive(current_path: str, depth: int = 0):
            "Recursively walk directories"
            if max_depth is not None and depth > max_depth:
                return

            try:
                items = self.listdir(current_path)
            except (FileNotFoundError, FSError):
                return

            for item in items:
                item_path = os.path.join(current_path, item).replace('\\', '/')

                try:
                    is_dir = self.isdir(item_path)

                    # Handle directories
                    if is_dir:
                        # Recurse into directory unless excluded
                        if not should_exclude(item, exclude):
                            yield from walk_recursive(item_path, depth + 1)
                    else:
                        # Handle files
                        if not should_exclude(item, exclude) and matches_filter(item, filter):
                            yield FSPath(item_path, root_fs=self)
                except (FileNotFoundError, FSError):
                    continue

        yield from walk_recursive(path, 0)

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
        for file_path in self.find_files(filter=filter, exclude=exclude, max_depth=max_depth):
            try:
                with file_path.open("rb") as f:
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
                                        "path": file_path.path,  # file path
                                    }
                                )
                        else:
                            for row, context, context_first_row in prepare_search_context(f, matches, search_context):
                                result.append(
                                    {
                                        "row_number": row,  # matching row number
                                        "context_first_row": context_first_row,  # context first row number
                                        "context": context,  # context
                                        "path": file_path.path,  # file path
                                    }
                                )
            except (OSError, IOError, FSError):
                pass

        return result


def prepare_search_context(f, matches, search_context) -> Generator[Tuple[int, str, int], None, None]:
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


class FSPath:

    def __init__(self, *parts: str, root_fs: RootFS) -> None:
        self.root_fs = root_fs
        if parts:
            self.path = os.path.join("/", *parts)
        else:
            self.path = "/"

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
    def parent(self) -> "FSPath":
        "The logical parent of the path"
        return FSPath(split(self.path)[0], root_fs=self.root_fs)

    def touch(self, mode=0o666, exist_ok=True) -> None:
        "Create this file"
        self.root_fs.touch(self.path)

    def rmdir(self) -> None:
        "Remove this directory"
        self.root_fs.rmdir(self.path)

    def unlink(self, missing_ok: bool = False) -> None:
        "Remove this file"
        try:
            self.root_fs.remove(self.path)
        except FileNotFoundError as ex:
            if not missing_ok:
                raise ex

    def delete(self) -> None:
        "Remove this file or directory"
        if self.is_dir():
            self.rmdir()
        else:
            self.unlink()

    def stat(self) -> os.stat_result:
        "File stat"
        info = self.root_fs.info(self.path)
        return os.stat_result(
            (
                info["mode"],
                info["ino"],
                None,
                info["nlink"],
                info["uid"],
                info["gid"],
                info["size"],
                None,
                info["mtime"],
                info["created"],
            )
        )

    def is_dir(self) -> bool:
        "Return True if this path is a directory"
        try:
            return self.root_fs.isdir(self.path)
        except Exception:
            return False

    def resolve(self) -> "FSPath":
        "Make the path absolute"
        return FSPath(os.path.realpath(self.path), root_fs=self.root_fs)

    def exists(self) -> bool:
        "Check if this path exists"
        return self.root_fs.exists(self.path)

    def iterdir(self, show_ignored_entries=False) -> Generator["FSPath", None, None]:
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
                yield FSPath(self.path, name, root_fs=self.root_fs)

    def size(self) -> Optional[int]:
        "Return file size for files and number of files for directories"
        try:
            if self.is_dir():
                return len(self.root_fs.listdir(self.path))
            else:
                return self.root_fs.size(self.path)
        except FSError:
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
        with self.root_fs.open(self.path, mode="rb") as f:
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
        local_path = self.root_fs.get_local_path(self.path)
        if local_path:
            # Local filesystem
            if as_attachment:
                # Send file as attachment (set Content-Disposition: attachment header)
                return send_file(
                    local_path,
                    as_attachment=True,
                    download_name=self.name,
                )
            else:
                return send_file(local_path)
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
            if isinstance(data, bytes):
                self.root_fs.write_text(self.path, data.decode('utf-8'))
            else:
                self.root_fs.write_text(self.path, str(data))
        else:
            if isinstance(data, str):
                self.root_fs.write_bytes(self.path, data.encode('utf-8'))
            else:
                self.root_fs.write_bytes(self.path, data)

    def read_text(self, encoding=None, errors=None) -> str:
        "Get the contents of a file as a string"
        return self.root_fs.read_text(self.path, encoding=encoding, errors=errors)

    def read_bytes(self) -> bytes:
        "Get the contents of a file as bytes"
        return self.root_fs.read_bytes(self.path)

    def __str__(self) -> str:
        return self.path

    def __repr__(self) -> str:
        return self.path

    def __truediv__(self, key) -> "FSPath":
        try:
            path = os.path.join(self.path, key)
            return FSPath(path, root_fs=self.root_fs)
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

    def __lt__(self, other: Any) -> bool:
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
