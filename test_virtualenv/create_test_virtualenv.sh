#!/usr/bin/env bash
cd "$(dirname "$0")"
source ./mo.sh
export AIRFLOW_HOME=${PWD}

export ENABLE_AIRFLOW_AUTH=1
export AIRFLOW_VERSION=1.10.12

function WEBSERVER_AUTH() {
    if [[ $ENABLE_AIRFLOW_AUTH == 1 ]]; then
        echo "authenticate = True"
        echo "rbac = True"
        echo "auth_backend = airflow.contrib.auth.backends.password_auth"
    else
        echo "authenticate = False"
        echo "rbac = False"
    fi
}

virtualenv -p `which python3` .
echo "export AIRFLOW_HOME=${AIRFLOW_HOME}" >> bin/activate
source bin/activate
pip install --upgrade pip

#export PYTHON_VERSION='3.7'
export PYTHON_VERSION=$(python3 -c "import sys; print('%s.%s' % (sys.version_info.major, sys.version_info.minor))")
pip install \
     apache-airflow[crypto,password]==${AIRFLOW_VERSION} \
      --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# pip install --no-deps airflow-code-editor
rm -rf plugins
mkdir -p plugins
ln -sf "${PWD}/../airflow_code_editor" plugins/airflow_code_editor

mo -u < airflow.cfg.tmpl > airflow.cfg
airflow initdb

if [[ $ENABLE_AIRFLOW_AUTH == 1 ]]; then
    # Create user 'admin' with password 'admin'
    airflow create_user -r Admin -u admin -e admin@example.com -f admin -l admin -p admin
fi
