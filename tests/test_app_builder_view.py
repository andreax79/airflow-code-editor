#!/usr/bin/env python

# from airflow import configuration
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder

from airflow_code_editor.app_builder_view import appbuilder_code_editor_view
from airflow_code_editor.commons import HTTP_200_OK, HTTP_400_BAD_REQUEST, ROUTE

app = Flask(__name__)
app.testing = True
app.config['SECRET_KEY'] = "000000000000000000000000"
db = SQLA(app)
appbuilder = AppBuilder(app, db.session)
appbuilder.add_view_no_menu(appbuilder_code_editor_view)
appbuilder.sm.check_authorization = lambda *args, **kargs: True
client = app.test_client()


def get(path, *args, **kargs):
    with app.test_client() as client:
        return client.get(f"{ROUTE}{path}", *args, **kargs)


def post(path, *args, **kargs):
    with app.test_client() as client:
        return client.post(f"{ROUTE}{path}", *args, **kargs)


def test_ping():
    res = get("/ping")
    assert res.status_code == HTTP_200_OK
    assert len(res.json['value']) > 10


def test_tree():
    res = get("/tree")
    assert res.status_code == HTTP_200_OK
    assert res.json['value']
    assert 'files' in [x['id'] for x in res.json['value']]
    assert 'files/~airflow_home' in [x['id'] for x in res.json['value']]
    assert 'git' in [x['id'] for x in res.json['value']]


def test_tree_git():
    res = get("/tree/git")
    assert res.status_code == HTTP_200_OK
    assert res.json['value']


def test_tree_local_branches():
    res = get("/tree/local-branches")
    assert res.status_code == HTTP_200_OK
    assert res.json['value']


def test_tree_files():
    res = get("/tree/files")
    assert res.status_code == HTTP_200_OK
    assert res.json['value']


def test_repo():
    res = post("/repo")
    assert res.status_code == HTTP_400_BAD_REQUEST
