#!/usr/bin/env python

import os
import os.path
import stat
import airflow
import airflow.plugins_manager
from airflow import configuration
from flask import Flask
from unittest import TestCase, main
from airflow_code_editor.commons import PLUGIN_NAME
from airflow_code_editor.tree import (
    get_tree,
)

assert airflow.plugins_manager
app = Flask(__name__)


class TestTree(TestCase):
    def setUp(self):
        self.root_dir = os.path.dirname(os.path.realpath(__file__))
        configuration.conf.set(PLUGIN_NAME, 'git_init_repo', 'False')
        configuration.conf.set(PLUGIN_NAME, 'root_directory', self.root_dir)

    def test_tree(self):
        with app.app_context():
            t = get_tree()
            self.assertTrue(len(t) > 0)
            self.assertTrue('git' in (x['id'] for x in t))

    def test_tags(self):
        with app.app_context():
            t = get_tree("tags")
            self.assertIsNotNone(t)

    def test_local_branches(self):
        with app.app_context():
            t = get_tree("local-branches")
            self.assertIsNotNone(t)

    def test_remote_branches(self):
        with app.app_context():
            t = get_tree("remote-branches")
            self.assertIsNotNone(t)

    def test_files(self):
        with app.app_context():
            t = get_tree("files")
            self.assertTrue(
                len([x.get('id') for x in t if x.get('id') == 'test_utils.py']) == 1
            )
            t = get_tree("files/folder")
            self.assertTrue(len([x.get('id') for x in t if x.get('id') == '1']) == 1)

    def test_files_long(self):
        with app.app_context():
            t = get_tree("files", ["long"])
            self.assertEqual(
                len([x.get('id') for x in t if x.get('id') == 'folder']), 1
            )
            folder = [x for x in t if x.get('id') == 'folder'][0]
            self.assertFalse(folder['leaf'])
            self.assertEqual(folder['size'], 3)
            self.assertTrue(stat.S_ISDIR(folder['mode']))

            self.assertEqual(
                len([x.get('id') for x in t if x.get('id') == 'test_utils.py']), 1
            )
            test_utils = [x for x in t if x.get('id') == 'test_utils.py'][0]
            self.assertTrue(test_utils['leaf'])
            self.assertFalse(stat.S_ISDIR(test_utils['mode']))

            t = get_tree("files/folder", ["long"])
            self.assertEqual(len([x.get('id') for x in t if x.get('id') == '1']), 1)
            one = [x for x in t if x.get('id') == '1'][0]
            self.assertTrue(one['leaf'])

    def test_git(self):
        with app.app_context():
            t = get_tree("git/HEAD")
            self.assertTrue(t is not None)


class TestTreeGitDisabled(TestCase):
    def setUp(self):
        self.root_dir = os.path.dirname(os.path.realpath(__file__))
        configuration.conf.set(PLUGIN_NAME, 'git_init_repo', 'False')
        configuration.conf.set(PLUGIN_NAME, 'root_directory', self.root_dir)
        configuration.conf.set(PLUGIN_NAME, 'git_enabled', 'False')

    def test_tree(self):
        with app.app_context():
            t = get_tree()
            self.assertTrue(len(t) > 0)
            self.assertTrue('git' not in (x['id'] for x in t))
            t = get_tree("tags")
            self.assertEqual(t, [])
            t = get_tree("local-branches")
            self.assertEqual(t, [])
            t = get_tree("remote-branches")
            self.assertEqual(t, [])
            t = get_tree("files")
            self.assertTrue(
                len([x.get('id') for x in t if x.get('id') == 'test_utils.py']) == 1
            )
            t = get_tree("files/folder")
            self.assertTrue(len([x.get('id') for x in t if x.get('id') == '1']) == 1)


if __name__ == '__main__':
    main()
