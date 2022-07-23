#!/usr/bin/env python

import fs
from pathlib import Path
from flask import Flask
from airflow_code_editor.commons import PLUGIN_NAME
from airflow_code_editor.fs import split, RootFS
from airflow import configuration

app = Flask(__name__)


def test_split():
    assert split("/aaa/bb/c") == ("/aaa/bb", "c")
    assert split("/aaa/bb/") == ("/aaa", "bb")
    assert split("/") == ("/", "")
    assert split("ciccio") == ("/", "ciccio")
    assert split("") == ("/", "")


def test_parent():
    root_fs = RootFS()
    a = root_fs.path("/aaa/bbb/ccc")
    assert a.name == "ccc"
    assert a.parent == root_fs.path("/aaa/bbb")

    a = root_fs.path("aaa", "bbb")
    assert a.name == "bbb"
    assert a.parent == root_fs.path("/aaa")


def test_root_fs():
    root_dir = Path(__file__).parent
    configuration.conf.set(PLUGIN_NAME, 'git_init_repo', 'False')
    configuration.conf.set(PLUGIN_NAME, 'root_directory', str(root_dir))
    configuration.conf.set(PLUGIN_NAME, 'git_enabled', 'True')

    root_fs = RootFS()
    name = "/folder/root_fs_test_1"
    try:
        root_fs.remove(name)
    except fs.errors.ResourceNotFound:
        pass
    root_fs.writetext(name, "data")
    assert root_fs.readtext(name) == "data"
    root_fs.copy(name, name + ".new")
    assert root_fs.readtext(name + ".new") == "data"
    root_fs.remove(name)
    root_fs.remove(name + ".new")

    name = "/~logs/logs_test_2"
    try:
        root_fs.remove(name)
    except fs.errors.ResourceNotFound:
        pass
    try:
        root_fs.remove(name + ".new")
    except fs.errors.ResourceNotFound:
        pass
    root_fs.writetext(name, "data")
    assert root_fs.readtext(name) == "data"
    root_fs.copy(name, name + ".new")
    assert root_fs.readtext(name + ".new") == "data"
    assert len(root_fs.listdir("/~logs/"))
    root_fs.remove(name)
    root_fs.remove(name + ".new")


def test_mem():
    root_fs = RootFS()
    root_fs.mount("/~mem", "mem://")
    root_fs.path("/~mem/f.txt").write_file("data", is_text=True)
    root_fs.path("/~mem/f.bin").write_file(b"data", is_text=False)
