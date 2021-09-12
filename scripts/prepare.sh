#!/usr/bin/env bash
set -e

export CURRENT_DIR=`realpath $(dirname "$0")`
export PARENT_DIR=`dirname "$CURRENT_DIR"`

export AIRFLOW_HOME="${AIRFLOW_HOME:-${CURRENT_DIR}/venv}"

source "${CURRENT_DIR}/mo.sh"

export ENABLE_AIRFLOW_AUTH="${ENABLE_AIRFLOW_AUTH:-1}"
# export AIRFLOW_VERSION=1.10.12
export AIRFLOW_VERSION="${AIRFLOW_VERSION:-2.1.3}"
# export FORCE_PYTHON_VERSION=3.7
export CONSTRAINTS_VERSION="${CONSTRAINTS_VERSION:-${AIRFLOW_VERSION}}"

export AIRFLOW_MAJOR_VERSION=${AIRFLOW_VERSION:0:1}
if [[ "${AIRFLOW_MAJOR_VERSION}" == "2" ]]; then
    export EXTRAS="password"
else
    export EXTRAS="crypto,password"
fi

function WEBSERVER_AUTH() {
    if [[ "${ENABLE_AIRFLOW_AUTH}" == "1" ]]; then
        echo "authenticate = True"
        echo "rbac = True"
        echo "auth_backend = airflow.contrib.auth.backends.password_auth"
    else
        echo "authenticate = False"
        echo "rbac = False"
    fi
}

export PYTHON_VERSION=$(python3 -c "import sys; print('%s.%s' % (sys.version_info.major, sys.version_info.minor))")
pip install \
      "apache-airflow[${EXTRAS}]==${AIRFLOW_VERSION}" \
      --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${CONSTRAINTS_VERSION}/constraints-${PYTHON_VERSION}.txt" \
      -r "${PARENT_DIR}/requirements.txt" \
      -r "${PARENT_DIR}/requirements-dev.txt"

if [ ! -d "${AIRFLOW_HOME}" ]; then
  mkdir -p "${AIRFLOW_HOME}"
fi

if [[ "${AIRFLOW_MAJOR_VERSION}" == "1" ]]; then
    mo -u < "${CURRENT_DIR}/airflow1.cfg.tmpl" > "${AIRFLOW_HOME}/airflow.cfg"
    airflow initdb
else
    mo -u < "${CURRENT_DIR}/airflow2.cfg.tmpl" > "${AIRFLOW_HOME}/airflow.cfg"
    airflow db init
fi

if [[ "${ENABLE_AIRFLOW_AUTH}" == "1" ]]; then
    # Create user 'admin' with password 'admin'
    if [[ "${AIRFLOW_MAJOR_VERSION}" == "1" ]]; then
        airflow create_user -r Admin -u admin -e admin@example.com -f admin -l admin -p admin
    else
        airflow users create -r Admin -u admin -e admin@example.com -f admin -l admin -p admin
    fi
fi

ln -sf "${CURRENT_DIR}/dags" "${AIRFLOW_HOME}/dags"
