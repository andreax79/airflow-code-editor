#!/usr/bin/env bash
set -e

export CURRENT_DIR=`realpath $(dirname "$0")`
export PARENT_DIR=`dirname "$CURRENT_DIR"`
source "${CURRENT_DIR}/config.sh"

export AIRFLOW_VERSION="${AIRFLOW_VERSION:-2.5.2}"
export CONSTRAINTS_VERSION="${CONSTRAINTS_VERSION:-${AIRFLOW_VERSION}}"
export AIRFLOW_EXTRAS="password"
export PYTHON_VERSION=$(python3 -c "import sys; print('%s.%s' % (sys.version_info.major, sys.version_info.minor))")

echo "--------------------------------------------------------------------------------"
env
echo "--------------------------------------------------------------------------------"

pip install \
      "apache-airflow[${AIRFLOW_EXTRAS}]==${AIRFLOW_VERSION}" \
      --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${CONSTRAINTS_VERSION}/constraints-${PYTHON_VERSION}.txt" \
      -r "${PARENT_DIR}/requirements.txt" \
      -r "${PARENT_DIR}/requirements-dev.txt"

if [ ! -d "${AIRFLOW_HOME}" ]; then
  mkdir -p "${AIRFLOW_HOME}"
fi

# Init airflow db
airflow db init
# Create user 'admin' with password 'admin'
airflow users create -r Admin -u admin -e admin@example.com -f admin -l admin -p admin

ln -sf "${CURRENT_DIR}/dags" "${AIRFLOW_HOME}/dags"
