# Scripts

- activate.sh (call config.sh, create_test_virtualenv.sh and install.sh) - activate virtual environment
- airflow.sh (call activate.sh) - prepare the virtual environment if required and start airflow
- config.sh - set environment variables
- coverage.sh (call activate.sh) - run tests coverage
- create_test_virtualenv.sh (call prepare.sh) - create the virtual environment
- destroy_test_virtualenv.sh - destroy the virtual environment
- install.sh (called by github workflows)
- tests.sh (call activate.sh) - run tests
- prepare.sh (called by github workflows, call config.sh) - prepare virtual environment
- mo.sh - mustache template rendering library
