#!/usr/bin/env python

from unittest import TestCase

from airflow import configuration

from airflow_code_editor.presigned import create_presigned, decode_presigned


class TestPresigned(TestCase):

    def setUp(self):
        configuration.conf.set("core", "fernet_key", "SECRET_KEY")

    def test_presigned(self):
        filename = "/README.md"
        tmp = create_presigned(filename, expires_in=10)
        assert decode_presigned(tmp) == filename
