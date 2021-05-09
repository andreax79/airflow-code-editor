#!/usr/bin/env bash
set -e

export CURRENT_DIR=`realpath $(dirname "$0")`
export PARENT_DIR=`dirname "$CURRENT_DIR"`

if [[ ! -a "${CURRENT_DIR}/venv/bin/activate" ]]; then
    source "${CURRENT_DIR}/create_test_virtualenv.sh"
fi

source "${CURRENT_DIR}/venv/bin/activate"
source "${CURRENT_DIR}/install.sh"
