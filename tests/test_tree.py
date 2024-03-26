#!/usr/bin/env python

import os
import stat
from pathlib import Path
from unittest import TestCase

import airflow
import airflow.plugins_manager
from airflow import configuration
from flask import Flask

from airflow_code_editor.commons import PLUGIN_NAME
from airflow_code_editor.tree import get_stat, get_tree

assert airflow.plugins_manager
app = Flask(__name__)


class TestTree(TestCase):
    def setUp(self):
        self.root_dir = Path(__file__).parent
        configuration.conf.set(PLUGIN_NAME, "git_init_repo", "False")
        configuration.conf.set(PLUGIN_NAME, "root_directory", str(self.root_dir))

    def test_tree(self):
        with app.app_context():
            t = get_tree()
            assert len(t) > 0
            assert "git" in (x["id"] for x in t)

    def test_tags(self):
        with app.app_context():
            t = get_tree("tags")
            assert t is not None

    def test_local_branches(self):
        with app.app_context():
            t = get_tree("local-branches")
            assert t is not None

    def test_remote_branches(self):
        with app.app_context():
            t = get_tree("remote-branches")
            assert t is not None

    def test_files(self):
        with app.app_context():
            t = get_tree("files")
            assert len([x.get("id") for x in t if x.get("id") == "test_utils.py"]) == 1
            t = get_tree("files/folder")
            assert len([x.get("id") for x in t if x.get("id") == "1"]) == 1

    def test_files_long(self):
        with app.app_context():
            t = get_tree("files", {"long": "true"})
            assert len([x.get("id") for x in t if x.get("id") == "folder"]) == 1
            folder = [x for x in t if x.get("id") == "folder"][0]
            assert not folder["leaf"]
            assert folder["size"] == 5
            assert stat.S_ISDIR(folder["mode"])

            self.assertEqual(len([x.get("id") for x in t if x.get("id") == "test_utils.py"]), 1)
            test_utils = [x for x in t if x.get("id") == "test_utils.py"][0]
            assert test_utils["leaf"]
            assert not stat.S_ISDIR(test_utils["mode"])

            t = get_tree("files/folder", {"long": "true"})
            assert len([x.get("id") for x in t if x.get("id") == "1"]) == 1
            one = [x for x in t if x.get("id") == "1"][0]
            assert one["leaf"]

    def test_git(self):
        with app.app_context():
            t = get_tree("git/HEAD")
            assert t is not None


class TestTreeGitDisabled(TestCase):
    def setUp(self):
        self.root_dir = Path(__file__).parent
        configuration.conf.set(PLUGIN_NAME, "git_init_repo", "False")
        configuration.conf.set(PLUGIN_NAME, "root_directory", str(self.root_dir))
        configuration.conf.set(PLUGIN_NAME, "git_enabled", "False")
        os.environ["GIT_AUTHOR_NAME"] = os.environ["GIT_COMMITTER_NAME"] = "git_author_name"
        os.environ["GIT_AUTHOR_EMAIL"] = os.environ["GIT_COMMITTER_EMAIL"] = "git_author_email"

    def test_tree(self):
        with app.app_context():
            t = get_tree()
            assert len(t) > 0
            assert "git" not in (x["id"] for x in t)
            t = get_tree("tags")
            assert t == []
            t = get_tree("local-branches")
            assert t == []
            t = get_tree("remote-branches")
            assert t == []
            t = get_tree("files")
            print(t)
            assert len([x.get("id") for x in t if x.get("id") == "test_utils.py"]) == 1
            t = get_tree("files/folder")
            assert len([x.get("id") for x in t if x.get("id") == "1"]) == 1


class TestStat(TestCase):
    def setUp(self):
        self.root_dir = Path(__file__).parent
        configuration.conf.set(PLUGIN_NAME, "git_init_repo", "False")
        configuration.conf.set(PLUGIN_NAME, "root_directory", str(self.root_dir))

    def test_tree(self):
        with app.app_context():
            t = get_stat()
            print(t)
            assert t is not None
            assert t["id"] is None
            assert t["exists"]
            assert not t["leaf"]

    def test_tags(self):
        with app.app_context():
            t = get_stat("tags")
            assert t is not None
            assert t["id"] == "tags"
            assert t["exists"]
            assert not t["leaf"]

    def test_local_branches(self):
        with app.app_context():
            t = get_stat("local-branches")
            assert t is not None
            assert t["id"] == "local-branches"
            assert t["exists"]
            assert not t["leaf"]

    def test_remote_branches(self):
        with app.app_context():
            t = get_stat("remote-branches")
            assert t is not None
            assert t["id"] == "remote-branches"
            assert t["exists"]
            assert not t["leaf"]

    def test_files(self):
        with app.app_context():
            t = get_stat("files")
            assert t is not None
            assert t["id"] == "files"
            assert t["exists"]
            assert not t["leaf"]

            t = get_stat("files/test_utils.py")
            assert t is not None
            assert t["id"] == "files/test_utils.py"
            assert t["exists"]
            assert t["leaf"]

            t = get_stat("files/not-found")
            assert t is not None
            assert not t["exists"]
            assert t["leaf"] is None

    def test_files_folder(self):
        with app.app_context():
            t = get_stat("files/folder")
            assert t is not None
            assert t["id"] == "files/folder"
            assert t["exists"]
            assert not t["leaf"]

            t = get_stat("files/folder/1")
            assert t is not None
            assert t["id"] == "files/folder/1"
            assert t["exists"]
            assert t["leaf"]

            t = get_stat("files/folder/not-found")
            assert t is not None
            assert not t["exists"]
            assert t["leaf"] is None
