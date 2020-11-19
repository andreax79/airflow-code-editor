#!/usr/bin/env python

import airflow

try:
    from flask_appbuilder import has_access
except (ImportError, ModuleNotFoundError):

    def has_access(x):
        return x


__all__ = ['has_access']
