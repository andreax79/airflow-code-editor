#!/usr/bin/env bash
export CURRENT_DIR=`realpath $(dirname "$0")`
export PARENT_DIR=`dirname "$CURRENT_DIR"`
source "${CURRENT_DIR}/config.sh"

if [[ ! -a "${CURRENT_DIR}/venv/bin/activate" ]]; then
    bash "${CURRENT_DIR}/create_test_virtualenv.sh"
fi

source "${CURRENT_DIR}/venv/bin/activate"
bash "${CURRENT_DIR}/install.sh"

if ! compgen -G "${PARENT_DIR}/dist/*.whl" > /dev/null; then
    export PYTHONPATH="${PARENT_DIR}:${PYTHONPATH}"
fi
