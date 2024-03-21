#!/usr/bin/env python

import shutil
from pathlib import Path

import fs
from airflow import configuration
from flask import Flask

from airflow_code_editor.commons import PLUGIN_NAME
from airflow_code_editor.fs import RootFS, split

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
    root_dir = "/tmp/tests"
    shutil.rmtree(root_dir, ignore_errors=True)
    shutil.copytree(Path(__file__).parent, root_dir)
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


def test_find():
    root_dir = "/tmp/tests"
    shutil.rmtree(root_dir, ignore_errors=True)
    shutil.copytree(Path(__file__).parent, root_dir)
    configuration.conf.set(PLUGIN_NAME, 'git_init_repo', 'False')
    configuration.conf.set(PLUGIN_NAME, 'root_directory', str(root_dir))
    configuration.conf.set(PLUGIN_NAME, 'git_enabled', 'True')

    root_fs = RootFS()
    name = "/folder/root_fs_test_1"
    t = list(root_fs.find_files())
    assert [path for path in t if path.name.startswith(".")]
    t = list(root_fs.find_files(exclude=[]))
    assert [path for path in t if path.name.startswith(".")]
    exclude = [".*", "__pycache__"]
    t = list(root_fs.find_files(exclude=exclude))
    assert not [path for path in t if path.name.startswith(".")]
    t = list(root_fs.find_files(path="/folder", exclude=exclude))
    assert len(t) == 3
    t = list(root_fs.find_files(path="/folder", filter="3*", exclude=exclude))
    assert len(t) == 1
