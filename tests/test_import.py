#!/usr/bin/env python

import airflow
import airflow.plugins_manager


def test_plugin_manager():
    assert airflow.plugins_manager


def test_import_commons():
    import airflow_code_editor.commons

    assert airflow_code_editor.commons


def test_import_app_builder_view():
    import airflow_code_editor.app_builder_view

    assert airflow_code_editor.app_builder_view


def test_import_api():
    import airflow_code_editor.api.api

    assert airflow_code_editor.api.api


def test_import_airflow_code_editor():
    import airflow_code_editor.airflow_code_editor

    assert airflow_code_editor.airflow_code_editor
