#!/usr/bin/env python

import airflow
import airflow.plugins_manager


def test_plugin_manager():
    assert airflow.plugins_manager


def test_import_auth():
    import airflow_code_editor.auth

    assert airflow_code_editor.auth


def test_import_commons():
    import airflow_code_editor.commons

    assert airflow_code_editor.commons


def test_import_flask_admin_view():
    import airflow_code_editor.flask_admin_view

    assert airflow_code_editor.flask_admin_view


def test_import_app_builder_view():
    import airflow_code_editor.app_builder_view

    assert airflow_code_editor.app_builder_view


def test_import_code_editor_view():
    import airflow_code_editor.code_editor_view

    assert airflow_code_editor.code_editor_view


def test_import_airflow_code_editor():
    import airflow_code_editor.airflow_code_editor

    assert airflow_code_editor.airflow_code_editor
