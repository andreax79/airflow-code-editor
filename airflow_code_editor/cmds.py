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
import logging
import subprocess
import threading
import shlex
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from flask import make_response, Response
from flask_login import current_user  # type: ignore
from airflow_code_editor import fs
from airflow_code_editor.commons import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    SUPPORTED_GIT_COMMANDS,
    GitOutput,
)
from airflow_code_editor.utils import (
    git_enabled,
    get_plugin_boolean_config,
    get_plugin_config,
    get_root_folder,
    normalize_path,
)

__all__ = [
    'execute_git_command',
]


def init_git_repo() -> None:
    "Initialize the git repository in root folder"
    cwd: str = get_root_folder()
    if (
        git_enabled()
        and not os.path.exists(os.path.join(cwd, '.git'))
        and get_plugin_boolean_config('git_init_repo')
    ):
        git_call(['init', '.'])
        gitignore = os.path.join(cwd, '.gitignore')
        if not os.path.exists(gitignore):
            with open(gitignore, 'w') as f:
                f.write('__pycache__\n')
            git_call(['add', '.gitignore'])
        git_call(['commit', '-m', 'Initial commit'])


def prepare_git_env() -> Dict[str, str]:
    "Prepare the environ for git"
    env = dict(os.environ)
    # Author
    git_author_name = get_plugin_config('git_author_name')
    if not git_author_name:
        try:
            git_author_name = '%s %s' % (
                current_user.first_name,
                current_user.last_name,
            )
        except Exception:
            pass
    if git_author_name:
        env['GIT_AUTHOR_NAME'] = git_author_name
        env['GIT_COMMITTER_NAME'] = git_author_name
    # Email
    git_author_email = get_plugin_config('git_author_email')
    if not git_author_email:
        try:
            git_author_email = current_user.email
        except Exception:
            pass
    if git_author_email:
        env['GIT_AUTHOR_EMAIL'] = git_author_email
        env['GIT_COMMITTER_EMAIL'] = git_author_email
    return env


def prepare_git_response(
    git_cmd: Optional[str],
    result: GitOutput = None,
    stderr: GitOutput = None,
    returncode: int = 0,
) -> Response:
    if result is None:
        result = stderr
    elif stderr:
        result = result + stderr
    if git_cmd == 'cat-file':
        response = make_response(
            result, HTTP_200_OK if returncode == 0 else HTTP_404_NOT_FOUND
        )
        response.headers['Content-Type'] = 'text/plain'
    else:
        response = make_response(result)
        response.headers['X-Git-Return-Code'] = str(returncode)
        response.headers['X-Git-Stderr-Length'] = str(len(stderr or ''))
        response.headers['Content-Type'] = 'text/plain'
    return response


_execute_git_command_lock = threading.Lock()


def execute_git_command(git_args: List[str]) -> Response:
    with _execute_git_command_lock:
        logging.info(' '.join(git_args))
        git_cmd = git_args[0] if git_args else None
        stdout: GitOutput = None
        stderr: GitOutput = None
        returncode = 0
        try:
            # Init git repo
            init_git_repo()
            # Local commands
            if git_cmd in LOCAL_COMMANDS:
                handler = LOCAL_COMMANDS[git_cmd]
                stdout = handler(git_args)
            # Git commands
            elif git_cmd in SUPPORTED_GIT_COMMANDS:
                git_default_args = shlex.split(get_plugin_config('git_default_args'))
                returncode, stdout, stderr = git_call(
                    git_default_args + git_args, capture_output=True
                )
            else:
                stdout = None
                stderr = bytes(
                    'Command not supported: git %s' % ' '.join(git_args), 'utf-8'
                )
                returncode = 1
        except OSError as ex:
            logging.error(ex)
            stdout = None
            stderr = ex.strerror
            returncode = ex.errno
        except Exception as ex:
            logging.error(ex)
            stdout = None
            stderr = ex.message
            returncode = 1
        finally:
            return prepare_git_response(git_cmd, stdout, stderr, returncode)


def git_ls_local(git_args: List[str]) -> str:
    "'git ls-tree' like output for local folders"
    long_ = False
    if '-l' in git_args or '--long' in git_args:
        git_args = [arg for arg in git_args if arg not in ('-l', '--long')]
        long_ = True
    path = git_args[1] if len(git_args) > 1 else ''
    path = normalize_path(path.split('#', 1)[0])
    result = []
    for name in sorted(fs.listdir(path)):
        if name.startswith('.') or name == '__pycache__':
            continue
        fullname = os.path.join(path, name)
        s = fs.stat(fullname)
        if fs.isdir(fullname):
            type_ = 'tree'
            try:
                size_: Optional[int] = len(fs.listdir(fullname))
            except Exception:
                size_ = None
        else:
            type_ = 'blob'
            size_ = s.st_size
        relname = os.path.join('/', path, name)  # fullname[len(cwd):]
        if long_:
            mtime = datetime.utcfromtimestamp(s.st_mtime).isoformat()[:16]
            result.append(
                '%06o %s %s#%s %8s\t%s'
                % (s.st_mode, type_, relname, mtime, size_, name)
            )
        else:
            result.append('%06o %s %s\t%s' % (s.st_mode, type_, relname, name))
    return '\n'.join(result)


def git_mounts(git_args: List[str]) -> str:
    "List mountpoints"
    return '\n'.join(sorted(fs.get_mount_points().keys()))


def git_rm_local(git_args: List[str]) -> str:
    "Delete local files/directories"
    for arg in git_args[1:]:
        if arg:
            if fs.isdir(arg):
                fs.rmdir(arg)
            else:
                fs.unlink(arg)
    return ''


def git_mv_local(git_args: List[str]) -> str:
    "Rename/Move local files"
    if len(git_args) < 3:
        raise Exception('Missing source/destination args')
    target = git_args[-1]
    for arg in git_args[1:-1]:
        fs.move(arg, target)
    return ''


LOCAL_COMMANDS = {
    'mounts': git_mounts,
    'ls-local': git_ls_local,
    'rm-local': git_rm_local,
    'mv-local': git_mv_local,
}


def git_call(
    argv: List[str], capture_output: bool = False
) -> Tuple[int, GitOutput, GitOutput]:
    "Run git command. If capture_output is true, stdout and stderr will be captured."
    if not git_enabled():
        return 1, '', 'Git is disabled'
    cmd: List[str] = [get_plugin_config('git_cmd')] + argv
    cwd: str = get_root_folder()
    env: Dict[str, str] = prepare_git_env()
    if capture_output:
        git = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            env=env,
        )
        stdout, stderr = git.communicate()
        returncode: int = git.returncode
    else:
        stdout = b''
        stderr = b''
        returncode = subprocess.call(cmd, cwd=cwd, env=env)
    return returncode, stdout, stderr
