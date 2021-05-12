#!/usr/bin/env python

import os
import os.path
import shutil
import tempfile
import airflow
import airflow.plugins_manager
from airflow import configuration
from flask import Flask
from unittest import TestCase, main
from airflow_code_editor.commons import PLUGIN_NAME
from airflow_code_editor.utils import (
    get_root_folder,
    mount_points,
    normalize_path,
    execute_git_command,
)

assert airflow.plugins_manager
app = Flask(__name__)


class TestUtils(TestCase):
    def setUp(self):
        self.root_dir = os.path.dirname(os.path.realpath(__file__))
        configuration.conf.set(PLUGIN_NAME, 'git_init_repo', 'False')
        configuration.conf.set(PLUGIN_NAME, 'root_directory', self.root_dir)

    def test_get_root_folder(self):
        self.assertIsNotNone(get_root_folder())

    def test_mount_points_config(self):
        self.assertTrue('root' in mount_points)
        self.assertTrue('airflow_home' in mount_points)
        self.assertTrue('logs' in mount_points)

    def test_normalize_path(self):
        self.assertEqual(normalize_path(None), '')
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

    def test_mounts(self):
        with app.app_context():
            r = execute_git_command(['mounts'])
        t = r.data.decode('utf-8')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(t, 'airflow_home\nlogs')

    def test_ls_local_logs(self):
        with app.app_context():
            r = execute_git_command(['ls-local', '-l', '~logs'])
        t = r.data.decode('utf-8')
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(t)

    def test_ls_local_airflow_hone(self):
        with app.app_context():
            r = execute_git_command(['ls-local', '-l', '~airflow_home'])
        t = r.data.decode('utf-8')
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(t)
        for line in t.split('\n'):
            i = line.split()
            self.assertTrue(i[1] in ['tree', 'blob'])
            self.assertTrue(i[2].startswith('/~airflow_home/'))

    def test_ls_local_folder(self):
        with app.app_context():
            r = execute_git_command(['ls-local', '-l', 'folder'])
        t = r.data.decode('utf-8')
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(t)
        for line in t.split('\n'):
            i = line.split()
            self.assertEqual(i[1], 'blob')
            self.assertTrue(i[2].startswith('/folder/'))
            self.assertEqual(i[3], '2')
            self.assertTrue(i[4] in ['1', '2', '3'])

    def test_rm_local(self):
        try:
            source = os.path.join(self.root_dir, 'new.file')
            with open(source, 'w') as f:
                f.write('test')
            self.assertTrue(os.path.exists(source))
            with app.app_context():
                execute_git_command(['rm-local', 'new.file'])
            self.assertFalse(os.path.exists(source))
        finally:
            try:
                os.unlink(source)
            except Exception:
                pass

    def test_mv_local(self):
        try:
            source = os.path.join(self.root_dir, 'new.file')
            target = os.path.join(self.root_dir, 'folder', 'new.file')
            self.assertFalse(os.path.exists(target))
            with open(source, 'w') as f:
                f.write('test')
            with app.app_context():
                execute_git_command(['mv-local', 'new.file', 'folder'])
            self.assertTrue(os.path.exists(target))
        finally:
            try:
                os.unlink(source)
            except Exception:
                pass
            try:
                os.unlink(target)
            except Exception:
                pass


class TestInitGitRepo(TestCase):
    def setUp(self):
        self.root_dir = tempfile.mkdtemp()
        configuration.conf.set(PLUGIN_NAME, 'git_init_repo', 'True')
        configuration.conf.set(PLUGIN_NAME, 'root_directory', self.root_dir)

    def tearDown(self):
        shutil.rmtree(self.root_dir)

    def test_ls_tree(self):
        with app.app_context():
            r = execute_git_command(['ls-tree', 'HEAD', '-l'])
        t = r.data.decode('utf-8')
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(t)


if __name__ == '__main__':
    main()
