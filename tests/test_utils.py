#!/usr/bin/env python

import airflow
import airflow.plugins_manager
from flask import Flask
from unittest import TestCase, main
from airflow_code_editor.utils import (
    get_root_folder,
    normalize_path,
    execute_git_command
)
assert(airflow.plugins_manager)
app = Flask(__name__)

class TestUtils(TestCase):

    def test_get_root_folder(self):
        self.assertIsNotNone(get_root_folder())

    def test_normalize_path(self):
        self.assertEqual(normalize_path('/'), '')
        self.assertEqual(normalize_path('/../'), '')
        self.assertEqual(normalize_path('../'), '')
        self.assertEqual(normalize_path('../../'), '')
        self.assertEqual(normalize_path('../..'), '')
        self.assertEqual(normalize_path('/..'), '')

        self.assertEqual(normalize_path('//'), '')
        self.assertEqual(normalize_path('////../'), '')
        self.assertEqual(normalize_path('..///'), '')
        self.assertEqual(normalize_path('..///../'), '')
        self.assertEqual(normalize_path('..///..'), '')
        self.assertEqual(normalize_path('//..'), '')

        self.assertEqual(normalize_path('/aaa'), 'aaa')
        self.assertEqual(normalize_path('/../aaa'), 'aaa')
        self.assertEqual(normalize_path('../aaa'), 'aaa')
        self.assertEqual(normalize_path('../../aaa'), 'aaa')
        self.assertEqual(normalize_path('../../aaa'), 'aaa')
        self.assertEqual(normalize_path('/../aaa'), 'aaa')

        self.assertEqual(normalize_path('/aaa'), 'aaa')
        self.assertEqual(normalize_path('aaa'), 'aaa')

    def test_invalid_command(self):
        with app.app_context():
            r = execute_git_command(['invalid-command'])
        t = r.data.decode('utf-8')
        self.assertEqual(r.status_code, 200)
        self.assertTrue('Command not supported' in t)

    def test_ls_tree(self):
        with app.app_context():
            r = execute_git_command(['ls-tree', 'HEAD', '-l'])
        t = r.data.decode('utf-8')
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(t)

    def test_ls_local(self):
        with app.app_context():
            r = execute_git_command(['ls-local', '-l'])
        t = r.data.decode('utf-8')
        print(t)
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(t)

if __name__ == '__main__':
    main()
