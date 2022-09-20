#!/usr/bin/env bash
set -e

export CURRENT_DIR=`realpath $(dirname "$0")`
source "${CURRENT_DIR}/activate.sh"

cd `dirname "$CURRENT_DIR"`
pytest --cov --cov-report=term-missing
