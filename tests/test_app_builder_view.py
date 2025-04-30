#!/usr/bin/env python

import pytest

from airflow_code_editor.utils import AIRFLOW_MAJOR_VERSION

if AIRFLOW_MAJOR_VERSION == 2:
    from airflow.www import app as application

    from airflow_code_editor.app_builder_view import appbuilder_code_editor_view
    from airflow_code_editor.commons import HTTP_200_OK, HTTP_400_BAD_REQUEST, ROUTE

    @pytest.fixture
    def app():
        return application.create_app(testing=True)

    @pytest.fixture
    def app_builder(app):
        appbuilder = app.appbuilder
        appbuilder.add_view_no_menu(appbuilder_code_editor_view)
        appbuilder.sm.check_authorization = lambda *args, **kargs: True
        return appbuilder

    def get(path, app, *args, **kargs):
        with app.test_client() as client:
            return client.get(f"{ROUTE}{path}", *args, **kargs)

    def post(path, app, *args, **kargs):
        with app.test_client() as client:
            return client.post(f"{ROUTE}{path}", *args, **kargs)

    def test_ping(app, app_builder):
        res = get("/ping", app)
        assert res.status_code == HTTP_200_OK
        assert len(res.json["value"]) > 10

    def test_tree(app, app_builder):
        res = get("/tree", app)
        assert res.status_code == HTTP_200_OK
        assert res.json["value"]
        assert "files" in [x["id"] for x in res.json["value"]]
        assert "files/~airflow_home" in [x["id"] for x in res.json["value"]]
        assert "git" in [x["id"] for x in res.json["value"]]

    def test_tree_git(app, app_builder):
        res = get("/tree/git", app)
        assert res.status_code == HTTP_200_OK
        assert res.json["value"]

    def test_tree_local_branches(app, app_builder):
        res = get("/tree/local-branches", app)
        assert res.status_code == HTTP_200_OK
        assert res.json["value"]

    def test_tree_files(app, app_builder):
        res = get("/tree/files", app)
        assert res.status_code == HTTP_200_OK
        assert res.json["value"]

    def test_repo(app, app_builder):
        res = post("/repo", app)
        assert res.status_code == HTTP_400_BAD_REQUEST

    def test_version(app, app_builder):
        res = get("/version", app)
        assert res.status_code == HTTP_200_OK
        assert "version" in res.json
        assert "airflow_version" in res.json
