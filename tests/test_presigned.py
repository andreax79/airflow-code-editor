#!/usr/bin/env python

from unittest import TestCase

from airflow_code_editor.presigned import create_presigned, decode_presigned
from airflow_code_editor.utils import conf


class TestPresigned(TestCase):

    def setUp(self):
        conf.set("core", "fernet_key", "SECRET_KEY")

    def test_presigned(self):
        filename = "/README.md"
        tmp = create_presigned(filename, expires_in=10)
        assert decode_presigned(tmp) == filename
