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

import cmd
import shlex
import sys

try:
    import readline
except ImportError:
    readline = None
from pathlib import Path

import platformdirs

from airflow_code_editor.commons import VERSION
from airflow_code_editor.fs import RootFS
from airflow_code_editor.utils import read_config_file

CONFIG_DIR = Path(platformdirs.user_config_dir(appname="CodeEditor"))
CONFIG_PATH = CONFIG_DIR / "config.ini"
HISTORY_PATH = ".sh_history"
HISTORY_SIZE = 1000

# Read the configuration
read_config_file(CONFIG_PATH)


class Shell(cmd.Cmd):
    intro = 'Type "help" list commands.\n'
    root_fs = RootFS()
    cwd = root_fs.path("/")

    def preloop(self):
        if readline is not None and CONFIG_PATH.exists():
            try:
                readline.read_history_file(HISTORY_PATH)
            except FileNotFoundError:
                pass

    def postloop(self):
        if readline is not None:
            readline.set_history_length(HISTORY_SIZE)
            readline.write_history_file(HISTORY_PATH)

    @property
    def prompt(self):
        return str(self.cwd) + "$ "

    def emptyline(self):
        "Do nothing on empty input line"
        pass

    def parseline(self, line):
        """Parse the line into a command name and a string containing
        the arguments.  Returns a tuple containing (command, args, line).
        'command' and 'args' may be None if the line couldn't be parsed.
        """
        parts = shlex.split(line)
        if parts:
            return parts[0], parts[1:], line
        else:
            return None, None, line

    def do_help(self, args):
        'List available commands with "help" or detailed help with "help cmd".'
        super().do_help(args[0] if args else None)

    def do_cd(self, args):
        "Change directory"
        if args:
            cwd = (self.cwd / args[0]).resolve()
        else:
            cwd = self.root_fs.path("/")
        if cwd.exists():
            self.cwd = cwd
        else:
            print("cd: no such file or directory: {cwd}".format(cwd=cwd))

    def do_cat(self, args):
        "Print file content"
        for arg in args:
            try:
                path = self.cwd / arg
                print(path.read_text())
            except Exception:
                print("cat: error")

    def do_pwd(self, args):
        "Print current directory"
        print(self.cwd)

    def do_ls(self, args):
        "List directory"
        for arg in args or ["."]:
            path = self.cwd / arg
            if not path.exists():
                print("ls: no such file or directory: {arg}".format(arg=arg))
            elif not path.is_dir():
                print(str(path.name))
            else:
                for item in path.iterdir():
                    if item.is_dir():
                        print(str(item.name) + "/")
                    else:
                        print(str(item.name))

    def do_mount(self, args):
        "List mountpoints or mount a filesystem"
        if len(args) == 2:
            try:
                self.root_fs.mount(args[1], args[0])
            except Exception as ex:
                print("mount: error: {message}".format(message=str(ex)))
        else:
            print("{0} on /".format(self.root_fs.default_fs))
            for item in self.root_fs.mounts:
                print(f"{item.filesystem} on {item.path}")

    def do_version(self, args):
        "Show version"
        print(VERSION)

    def do_exit(self, args):
        "Exit"
        return True

    def do_quit(self, args):
        "Exit"
        return True


def main():
    if sys.argv[1:]:
        line = " ".join(sys.argv[1:])
        return Shell().onecmd(line)
    try:
        Shell().cmdloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
