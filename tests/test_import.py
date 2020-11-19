#!/usr/bin/env python

import airflow
import airflow.plugins_manager
from unittest import TestCase, main

assert airflow.plugins_manager


class TestImport(TestCase):
    def test_import_auth(self):
        import airflow_code_editor.auth

        self.assertTrue(True)

    def test_import_commons(self):
        import airflow_code_editor.commons

        self.assertTrue(True)

    def test_import_flask_admin_view(self):
        import airflow_code_editor.flask_admin_view

        self.assertTrue(True)

    def test_import_app_builder_view(self):
        import airflow_code_editor.app_builder_view

        self.assertTrue(True)

    def test_import_code_editor_view(self):
        import airflow_code_editor.code_editor_view

        self.assertTrue(True)

    def test_import_airflow_code_editor(self):
        import airflow_code_editor.airflow_code_editor

        self.assertTrue(True)


if __name__ == "__main__":
    main()
