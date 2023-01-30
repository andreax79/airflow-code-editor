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

import fcntl
import logging
import os
import pty
import shlex
import select
import signal
import struct
import subprocess
import termios
import threading
from typing import Dict
from flask import Blueprint, request
from flask_sock import Sock
from simple_websocket import ConnectionClosed, Server
from airflow_code_editor.auth import has_access
from airflow_code_editor.commons import DEFAULT_SHELL, DEFAULT_TERM, ROUTE
from airflow_code_editor.utils import get_plugin_config, is_enabled, terminal_enabled

__all__ = [
    "init_webshell",
    "WebShell",
]


RESIZE = "\033[8;"
CLOSE = "\033$,F"
DEFAULT_COLUMNS = 80
DEFAULT_LINES = 24
WEBSOCKET_SELECT_TIMEOUT = 10

log = logging.getLogger(__name__)


class WebShell:
    def __init__(self, ws: Server, columns: int = DEFAULT_COLUMNS, lines: int = DEFAULT_LINES) -> None:
        self.ws = ws
        self.columns = columns or DEFAULT_COLUMNS
        self.lines = lines or DEFAULT_LINES
        self.running = False
        self.pid = -1

    def start(self) -> None:
        "Start processing input/output"
        # Start shell
        self.start_shell()
        # Start output thread
        self.process_output_thread = threading.Thread(target=self.process_output)
        self.process_output_thread.start()
        self.process_input()

    def start_shell(self) -> None:
        "Start shell"
        (master_fd, child_fd) = pty.openpty()
        cmd = shlex.split(get_plugin_config("terminal_shell") or os.environ.get("SHELL") or DEFAULT_SHELL)
        popen = subprocess.Popen(
            cmd,
            stdin=child_fd,
            stdout=child_fd,
            stderr=child_fd,
            env=self.prepare_environ(),
            preexec_fn=os.setsid,
            shell=False,
            close_fds=True,
        )
        self.pid = popen.pid
        self.running = True
        log.info(f"Start WebShell pid: {self.pid}")
        self.file = os.fdopen(master_fd, "w+b", 0)
        self.set_winsize()

    def set_winsize(self):
        winsize = struct.pack("HHHH", self.lines, self.columns, 0, 0)
        fcntl.ioctl(self.file.fileno(), termios.TIOCSWINSZ, winsize)

    def prepare_environ(self) -> Dict[str, str]:
        "Prepare shell environment"
        environ = dict(os.environ)
        environ["COLUMNS"] = str(self.columns)
        environ["LINES"] = str(self.lines)
        environ["TERM"] = DEFAULT_TERM
        return environ

    def process_input(self) -> None:
        "Send received keys to the child process"
        try:
            while self.running:
                data = self.ws.receive()
                if data is not None:
                    if data.startswith(RESIZE):
                        try:
                            t = data.split(";")
                            self.columns = int(t[1])
                            self.rows = int(t[2][:-1])
                            self.set_winsize()
                        except:
                            pass
                    elif data.startswith(CLOSE):
                        raise ConnectionClosed
                    else:
                        self.file.write(data.encode())
        except ConnectionClosed:
            log.info(f"WebShell process_input ConnectionClosed exception pid: {self.pid}")
        finally:
            self.close()

    def process_output(self) -> None:
        "Send process output to the WebSocket"
        try:
            while self.running:
                r, w, e = select.select([self.file], [], [], WEBSOCKET_SELECT_TIMEOUT)
                if self.file in r:
                    self.ws.send(os.read(self.file.fileno(), 65536))
                # self.ws.send(self.file.read(65536))
                # else:
                # self.ws.send('x')
                # from simple_websocket.ws import Ping
                # self.ws.sock.send(self.ws.ws.send(Ping()))
        except (ValueError, ConnectionClosed):
            pass

    def close(self) -> None:
        "Close shell"
        # Kill child process
        log.info(f"WebShell close pid: {self.pid}")
        try:
            os.kill(self.pid, signal.SIGKILL)
            os.waitpid(self.pid, 0)
            self.running = False
        except Exception as ex:
            log.error(f"WebShell kill error {ex} pid: {self.pid}")
            pass
        self.file.close()
        # Wait for process_output thread termination
        log.info(f"WebShell wait process_output_thread join {self.pid}")
        self.process_output_thread.join()
        log.info(f"WebShell process_output_thread join done {self.pid}")


@has_access
def ws(ws: Server) -> None:
    try:
        columns = int(request.args.get("columns"))
    except:
        columns = None
    try:
        lines = int(request.args.get("lines"))
    except:
        lines = None
    shell = WebShell(ws, columns, lines)
    shell.start()


def init_webshell(bp: Blueprint) -> None:
    if is_enabled() and terminal_enabled():
        sock = Sock()
        sock.route(f"{ROUTE}/ws", bp=bp)(ws)
