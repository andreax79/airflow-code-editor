#!/usr/bin/env python

__all__ = [
    'has_access',
    'BASE_PERMISSIONS',
]

try:
    # AppBuilder (Airflow >= 2.0)
    from airflow.www import auth
    from airflow.security import permissions

    PERMISSIONS = [
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_WEBSITE),
    ]

    BASE_PERMISSIONS = ["can_list", "can_create", "menu_acccess"]

    def has_access(*args):
        return auth.has_access(PERMISSIONS)(*args)

except (ImportError, ModuleNotFoundError):
    BASE_PERMISSIONS = ["can_list"]

    try:
        # AppBuilder (Airflow >= 1.10 < 2.0 and rbac = True)
        from airflow.www_rbac.decorators import has_dag_access

        def has_access(*args):
            return has_dag_access(can_dag_edit=True)

    except (ImportError, ModuleNotFoundError):
        # Flask Admin (Airflow < 2.0 and rbac = False)

        def has_access(x):
            return x
