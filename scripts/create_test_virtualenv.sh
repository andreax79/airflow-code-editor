#!/usr/bin/env bash
set -e

export CURRENT_DIR=`realpath $(dirname "$0")`
export PARENT_DIR=`dirname "$CURRENT_DIR"`

export AIRFLOW_HOME="${CURRENT_DIR}/venv"

virtualenv -p "$(which python${FORCE_PYTHON_VERSION:-3})" "${CURRENT_DIR}/venv"
echo "export AIRFLOW_HOME=${AIRFLOW_HOME}" >> "${CURRENT_DIR}/venv/bin/activate"

source "${CURRENT_DIR}/venv/bin/activate"
pip install --upgrade pip
pip install --upgrade wheel setuptools

source "${CURRENT_DIR}/prepare.sh"
