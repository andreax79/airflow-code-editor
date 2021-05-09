#!/usr/bin/env bash
set -e

export CURRENT_DIR=`realpath $(dirname "$0")`

rm -rf "${CURRENT_DIR}/venv"
