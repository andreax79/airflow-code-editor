#!/usr/bin/env bash
cd "$(dirname "$0")"
if [[ ! -a bin/activate ]]; then
    ./create_test_virtualenv.sh
fi
source bin/activate
./bin/airflow "$@"
