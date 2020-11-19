#!/usr/bin/env bash
cd "$(dirname "$0")" || exit 1
source ./mo.sh
export AIRFLOW_HOME=${PWD}

export ENABLE_AIRFLOW_AUTH=1
# export AIRFLOW_VERSION=1.10.12
export AIRFLOW_VERSION=2.0.0b2
# export FORCE_PYTHON_VERSION=3.7

export AIRFLOW_MAJOR_VERSION=${AIRFLOW_VERSION:0:1}
if [[ "${AIRFLOW_MAJOR_VERSION}" == "2" ]]; then
    export CONSTRAINTS_VERSION="2-0"
    export EXTRAS="password"
else
    export CONSTRAINTS_VERSION="${AIRFLOW_VERSION}"
    export EXTRAS="crypto,password"
fi

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

virtualenv -p "$(which python${FORCE_PYTHON_VERSION:-3})" .
echo "export AIRFLOW_HOME=${AIRFLOW_HOME}" >> bin/activate
source bin/activate
pip install --upgrade pip

export PYTHON_VERSION=$(python3 -c "import sys; print('%s.%s' % (sys.version_info.major, sys.version_info.minor))")
pip install \
     apache-airflow[${EXTRAS}]==${AIRFLOW_VERSION} \
      --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${CONSTRAINTS_VERSION}/constraints-${PYTHON_VERSION}.txt"

# pip install --no-deps airflow-code-editor
rm -rf plugins
mkdir -p plugins
# ln -sf "${PWD}/../airflow_code_editor" plugins/airflow_code_editor

if [[ "${AIRFLOW_MAJOR_VERSION}" == "1" ]]; then
    mo -u < airflow1.cfg.tmpl > airflow.cfg
    airflow initdb
else
    mo -u < airflow2.cfg.tmpl > airflow.cfg
    airflow db init
fi

if [[ $ENABLE_AIRFLOW_AUTH == 1 ]]; then
    # Create user 'admin' with password 'admin'
    if [[ "${AIRFLOW_MAJOR_VERSION}" == "1" ]]; then
        airflow create_user -r Admin -u admin -e admin@example.com -f admin -l admin -p admin
    else
        airflow users create -r Admin -u admin -e admin@example.com -f admin -l admin -p admin
    fi
fi
