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
from flask import make_response
from flask_login import current_user
from airflow import configuration
from airflow_code_editor.commons import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    SUPPORTED_GIT_COMMANDS
)

__all__ = [
    'normalize_path',
    'execute_git_command'
]

def normalize_path(path):
    comps = (path or '/').split('/')
    result = []
    for comp in comps:
        if comp in ('', '.'):
            pass
        elif (comp != '..' or (result and result[-1] == '..')):
            result.append(comp)
        elif result:
            result.pop()
    return '/'.join(result)

def prepare_response(git_cmd, result=None, stderr=None, returncode=0):
    if result is None:
        result = stderr
    elif stderr:
        result = result + stderr
    if git_cmd == 'cat-file':
        response = make_response(result, HTTP_200_OK if returncode == 0 else HTTP_404_NOT_FOUND)
        response.headers['Content-Type'] = 'text/plain'
    else:
        response = make_response(result)
        response.headers['X-Git-Return-Code'] = str(returncode)
        response.headers['X-Git-Stderr-Length'] = str(len(stderr or ''))
    return response

def prepare_git_env():
    " Prepare the environ for git "
    env = dict(os.environ)
    try:
        env['GIT_AUTHOR_NAME'] = '%s %s' % (current_user.first_name, current_user.last_name)
        env['GIT_AUTHOR_EMAIL'] = current_user.email
        env['GIT_COMMITTER_NAME'] = env['GIT_AUTHOR_NAME']
        env['GIT_COMMITTER_EMAIL'] = env['GIT_AUTHOR_EMAIL']
    except:
        pass
    finally:
        return env

_execute_git_command_lock = threading.Lock()

def execute_git_command(git_args):
    with _execute_git_command_lock:
        logging.info(' '.join(git_args))
        git_cmd = git_args[0] if git_args else None
        try:
            cwd = configuration.get('core', 'dags_folder')
            if not os.path.exists(os.path.join(cwd, '.git')):
                init_git_repo()
            if git_cmd == 'ls-local':
                stdout = git_ls_local(git_args)
                stderr = None
                returncode = 0
            elif git_cmd in SUPPORTED_GIT_COMMANDS:
                cmd = [ "git", "-c", "color.ui=true" ] + git_args
                git = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, env=prepare_git_env())
                stdout, stderr = git.communicate()
                returncode = git.returncode
            else:
                stdout = None
                stderr = 'Command not supported: git %s' % ' '.join(git_args)
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
            return prepare_response(git_cmd, stdout, stderr, returncode)

def git_ls_local(git_args):
    " 'git ls-tree -l' like output for local folders "
    cwd = configuration.get('core', 'dags_folder')
    path = git_args[2] if len(git_args) > 2 else ''
    dirpath = os.path.join(cwd, normalize_path(path))
    result = []
    for name in sorted(os.listdir(dirpath)):
        if name.startswith('.') or name == '__pycache__':
            continue
        fullname = os.path.join(dirpath, name)
        s = os.stat(fullname)
        if os.path.isdir(fullname):
            type_ = 'tree'
            size_ = '-'
        else:
            type_ = 'blob'
            size_ = s.st_size
        relname = fullname[len(cwd):]
        result.append('%06o %s %s %8s\t%s' % (s.st_mode, type_, relname, size_, name))
    return '\n'.join(result)

def init_git_repo():
    " Initialize the git repository in dag_folder "
    cwd = configuration.get('core', 'dags_folder')
    subprocess.call([ 'git', 'init', '.'], cwd=cwd)
    gitignore = os.path.join(cwd, '.gitignore')
    if not os.path.exists(gitignore):
        with open(gitignore, 'w') as f:
            f.write('__pycache__\n')
        subprocess.call([ 'git', 'add', '.gitignore' ], cwd=cwd)
    subprocess.call([ 'git', 'commit', '-m', 'Initial commit' ], cwd=cwd, env=prepare_git_env())

assert(normalize_path('/') == '')
assert(normalize_path('/../') == '')
assert(normalize_path('../') == '')
assert(normalize_path('../../') == '')
assert(normalize_path('../..') == '')
assert(normalize_path('/..') == '')

assert(normalize_path('//') == '')
assert(normalize_path('////../') == '')
assert(normalize_path('..///') == '')
assert(normalize_path('..///../') == '')
assert(normalize_path('..///..') == '')
assert(normalize_path('//..') == '')

assert(normalize_path('/aaa') == 'aaa')
assert(normalize_path('/../aaa') == 'aaa')
assert(normalize_path('../aaa') == 'aaa')
assert(normalize_path('../../aaa') == 'aaa')
assert(normalize_path('../../aaa') == 'aaa')
assert(normalize_path('/../aaa') == 'aaa')

assert(normalize_path('/aaa') == 'aaa')
assert(normalize_path('aaa') == 'aaa')

