#!/usr/bin/env python

__all__ = ['has_access']

try:
    from flask_appbuilder import has_access
except (ImportError, ModuleNotFoundError):

    def has_access(x):
        return x
