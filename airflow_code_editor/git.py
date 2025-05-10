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

import logging
import os
import shlex
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# TODO
from flask_login import current_user  # type: ignore

from airflow_code_editor.commons import (
    DEFAULT_GIT_BRANCH,
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    SUPPORTED_GIT_COMMANDS,
    GitOutput,
)
from airflow_code_editor.fs import RootFS
from airflow_code_editor.utils import (
    Response,
    get_plugin_boolean_config,
    get_plugin_config,
    get_root_folder,
    make_response,
    normalize_path,
    prepare_api_response,
    read_mount_points_config,
)

__all__ = [
    'git_enabled',
    'execute_git_command',
]


def git_enabled() -> bool:
    "Return true if git is enabled in the configuration"
    return get_plugin_boolean_config('git_enabled')


_execute_git_command_lock = threading.Lock()


class CompletedGitCommand:
    def __init__(
        self,
        args: List[str],
        returncode: int,
        stdout: GitOutput = None,
        stderr: GitOutput = None,
    ):
        self.args = args
        self.returncode = returncode
        if self.git_cmd == 'cat-file':
            self.stdout = stdout
            self.stderr = stderr
        else:
            self.stdout = stdout.decode('utf-8') if isinstance(stdout, bytes) else stdout
            self.stderr = stderr.decode('utf-8') if isinstance(stderr, bytes) else stderr

    @property
    def git_cmd(self):
        return self.args[0] if self.args else None

    def prepare_git_response(self) -> Response:
        if self.git_cmd == 'cat-file':
            response = make_response(
                content=self.stdout or self.stderr,
                status=HTTP_200_OK if self.returncode == 0 else HTTP_404_NOT_FOUND,
                mimetype='text/plain',
            )
        else:
            response = prepare_api_response(
                data=self.stdout,
                returncode=self.returncode,
                error_message=self.stderr or None,
            )
        return response


def execute_git_command(git_args: List[str]) -> CompletedGitCommand:
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
                returncode, stdout, stderr = git_call(git_default_args + git_args, capture_output=True)
            else:
                stdout = None
                stderr = 'Command not supported: git {0}'.format(' '.join(git_args))
                returncode = 1
            return CompletedGitCommand(git_args, returncode, stdout, stderr)
        except OSError as ex:
            logging.error(ex)
            stdout = None
            stderr = ex.strerror
            returncode = ex.errno
            return CompletedGitCommand(git_args, returncode, stdout, stderr)
        except Exception as ex:
            logging.error(ex)
            stdout = None
            stderr = ex.message if hasattr(ex, 'message') else str(ex)
            returncode = 1
            return CompletedGitCommand(git_args, returncode, stdout, stderr)


def git_ls_local(git_args: List[str]) -> str:
    "'git ls-tree' like output for local folders"
    long_ = False  # long format
    if '-l' in git_args or '--long' in git_args:
        git_args = [arg for arg in git_args if arg not in ('-l', '--long')]
        long_ = True
    all_ = False  # do not ignore entries
    if '-a' in git_args:
        git_args = [arg for arg in git_args if arg not in ('-a')]
        all_ = True
    path = git_args[1] if len(git_args) > 1 else ''
    path = normalize_path(path.split('#', 1)[0])
    result = []
    root_fs = RootFS()
    for item in root_fs.path(path).iterdir(show_ignored_entries=all_):
        if item.is_dir():
            type_ = 'tree'
        else:
            type_ = 'blob'
        s = item.stat()
        if long_:
            mtime = datetime.utcfromtimestamp(s.st_mtime).isoformat()[:16]
            result.append('%06o %s %s#%s %8s\t%s' % (s.st_mode, type_, str(item), mtime, item.size(), item.name))
        else:
            result.append('%06o %s %s\t%s' % (s.st_mode, type_, str(item), item.name))
    return '\n'.join(result)


def git_mounts(git_args: List[str]) -> str:
    "List mountpoints"
    mount_points = read_mount_points_config()
    return '\n'.join(sorted(k for k, v in mount_points.items() if not v.default))


def git_rm_local(git_args: List[str]) -> str:
    "Delete local files/directories"
    root_fs = RootFS()
    for arg in git_args[1:]:
        if arg:
            root_fs.path(arg).delete()
    return ''


def git_mv_local(git_args: List[str]) -> str:
    "Rename/Move local files"
    if len(git_args) < 3:
        raise Exception('Missing source/destination args')
    root_fs = RootFS()
    target = git_args[-1]
    for arg in git_args[1:-1]:
        source = root_fs.path(arg)
        source.move(target)
    return ''


def git_help(git_args: List[str]) -> str:
    "Show supported git commands"
    return '\n'.join(list(LOCAL_COMMANDS.keys()) + SUPPORTED_GIT_COMMANDS)


LOCAL_COMMANDS = {
    'help': git_help,
    'mounts': git_mounts,
    'ls-local': git_ls_local,
    'rm-local': git_rm_local,
    'mv-local': git_mv_local,
}


def git_call(argv: List[str], capture_output: bool = False) -> Tuple[int, bytes, bytes]:
    "Run git command. If capture_output is true, stdout and stderr will be captured."
    if not git_enabled():
        return 1, b'', b'git is disabled'
    cmd: List[str] = [get_plugin_config('git_cmd')] + argv
    cwd: Path = get_root_folder()
    env: Dict[str, str] = prepare_git_env()
    try:
        completed = subprocess.run(
            args=cmd,
            stdin=subprocess.PIPE if capture_output else None,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None,
            cwd=cwd,
            env=env,
        )
        return completed.returncode, completed.stdout, completed.stderr
    except (FileNotFoundError, PermissionError):
        return 127, b'', b'git command not found'


def get_default_branch() -> str:
    stdout = git_call(['config', '--global', 'init.defaultBranch'], capture_output=True)[1]
    default_branch = stdout.decode('utf8').strip('\n')
    return default_branch or DEFAULT_GIT_BRANCH


def init_git_repo() -> None:
    "Initialize the git repository in root folder"
    cwd: Path = get_root_folder()
    if git_enabled() and not (cwd / '.git').exists() and get_plugin_boolean_config('git_init_repo'):
        git_call(['init', '-b', get_default_branch(), '.'])
        gitignore = cwd / '.gitignore'
        if not gitignore.exists():
            with gitignore.open('w') as f:
                f.write('__pycache__\n')
            git_call(['add', '.gitignore'])
        git_call(['commit', '-m', 'Initial commit'])


def prepare_git_env() -> Dict[str, str]:
    "Prepare the environ for git"
    env = dict(os.environ)
    # Don't prompt on the terminal
    env['GIT_TERMINAL_PROMPT'] = '0'
    env['GIT_ASKPASS'] = '/bin/true'
    env['GIT_EDITOR'] = '/bin/false'
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
