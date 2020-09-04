#!/usr/bin/env python

import airflow
from functools import wraps

__all__ = [
    'login_required'
]


def login_required(func):
    # when airflow loads plugins, login is still None.
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if airflow.login:
            return airflow.login.login_required(func)(*args, **kwargs)
        return func(*args, **kwargs)
    return func_wrapper
