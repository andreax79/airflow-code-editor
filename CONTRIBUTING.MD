# Contributing

If you want to add an issue or pull request, please ensure that the [existing issues](https://github.com/andreax79/airflow-code-editor/issues?utf8=✓&q=)
don't already cover your question or contribution.

To get started contributing code to the `airflow-code-editor` project:

1. Fork the repo

2. Clone it on the local machine

  ```bash
    git clone https://github.com/andreax79/airflow-code-editor.git
    cd airflow-code-editor
  ```

3. Create and activate virtualenv

  ```bash
    source ./scripts/activate.sh
  ```

4. Make changes you need. Build npm package with:

  ```bash
    make npm-build
  ```

5. You can start Airflow webserver or scheduler with these commands:

  ```bash
    make webserver
    make scheduler
  ```

6. Run tests

  ```bash
    make test
  ```

7. Commit and push changes

  ```bash
    git add .
    git commit
    git push
  ```

7. Create [pull request](https://github.com/andreax79/airflow-code-editor/compare) to the original repo
