#!/usr/bin/env bash
cd "$(dirname "$0")"
if [[ ! -a bin/activate ]]; then
    ./create_test_virtualenv.sh
fi

source bin/activate

if compgen -G "../dist/*.whl" > /dev/null; then
    echo "Install plugin"
    pip install --no-deps ../dist/*.whl --force
    rm ../dist/*.whl
fi

./bin/airflow "$@"
