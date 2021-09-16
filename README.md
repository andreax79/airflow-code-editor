# Airflow Code Editor Plugin
A plugin for [Apache Airflow](https://github.com/apache/airflow) that allows you to edit DAGs in browser.
It provides a file managing interface within specified directories and it can be used to edit, upload, and download your files.
If git support is enabled, the DAGs are stored in a Git repository. You may use it to view Git history, review local changes and commit.

[![Build Status](https://github.com/andreax79/airflow-code-editor/workflows/Tests/badge.svg)](https://github.com/andreax79/airflow-code-editor/actions)
[![PyPI version](https://badge.fury.io/py/airflow-code-editor.svg)](https://badge.fury.io/py/airflow-code-editor)
[![PyPI](https://img.shields.io/pypi/pyversions/airflow-code-editor.svg)](https://pypi.org/project/airflow-code-editor)
[![Downloads](https://pepy.tech/badge/airflow-code-editor/month)](https://pepy.tech/project/airflow-code-editor)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

### System Requirements

* Airflow Versions
    * 1.10.3 or newer
* git Versions (git is not required if git support is disabled)
    * 2.0 or newer

### Screenshots

![File manager](https://user-images.githubusercontent.com/1288154/133688225-1a5e2298-bfb2-402f-999c-1126b4e4ceb5.png)

![Code editor](https://user-images.githubusercontent.com/1288154/133688469-96a0ae00-a1dd-4923-b09a-59cd41a5b4e7.png)

![Git tags](https://andreax79.github.io/airflow-code-editor/screenshots/3.png)

![Git workspace](https://andreax79.github.io/airflow-code-editor/screenshots/4.png)


### Install Instructions

1. Install the plugin

  ```bash
    pip install airflow-code-editor
  ```

2. (Optional) Install Black Python code formatter.

  ```bash
    pip install black
  ```

3. Restart the Airflow Web Server

4. Open Admin - DAGs Code Editor


### Config Options

You can set options editing the Airflow's configuration file or setting environment variables.
You can edit your *airflow.cfg* adding any of the following settings in the \[code_editor\] section.
All the settings are optional.

* **git_enabled**  enable git support (default: True). If git is not installed, disable this option.
* **git_cmd**  git command (path)
* **git_default_args**  git arguments added to each call (default: -c color.ui=true)
* **git_author_name** human-readable name in the author/committer (default logged user first and last names)
* **git_author_email** email for the author/committer (default: logged user email)
* **git_init_repo**  initialize a git repo in DAGs folder (default: True)
* **root_directory**  root folder (default: Airflow DAGs folder)
* **mount_name**, **mount1_name**, ...  configure additional file folder name (mount point)
* **mount_path**, **mount1_path**, ...  configure additional file path
* **line_length**  Python code formatter - max line length (default: 88)
* **string_normalization**  Python code formatter - if true normalize string quotes and prefixes (default: False)

Example:
```
   [code_editor]
   git_enabled = True
   git_cmd = /usr/bin/git
   git_default_args = -c color.ui=true
   git_init_repo = False
   root_directory = /home/airflow/dags
   line_length = 88
   string_normalization = False
   mount_name = data
   mount_path = /home/airflow/data
   mount1_name = logs
   mount1_path = /home/airflow/logs
```

You can also set options with the following environment variables:

* AIRFLOW__CODE_EDITOR__GIT_ENABLED
* AIRFLOW__CODE_EDITOR__GIT_CMD
* AIRFLOW__CODE_EDITOR__GIT_DEFAULT_ARGS
* AIRFLOW__CODE_EDITOR__GIT_AUTHOR_NAME
* AIRFLOW__CODE_EDITOR__GIT_AUTHOR_EMAIL
* AIRFLOW__CODE_EDITOR__GIT_INIT_REPO
* AIRFLOW__CODE_EDITOR__ROOT_DIRECTORY
* AIRFLOW__CODE_EDITOR__LINE_LENGTH
* AIRFLOW__CODE_EDITOR__STRING_NORMALIZATION
* AIRFLOW__CODE_EDITOR__MOUNT_NAME
* AIRFLOW__CODE_EDITOR__MOUNT_PATH
* AIRFLOW__CODE_EDITOR__MOUNT1_NAME, AIRFLOW__CODE_EDITOR__MOUNT2_NAME, ...
* AIRFLOW__CODE_EDITOR__MOUNT1_PATH, AIRFLOW__CODE_EDITOR__MOUNT2_PATH, ...

Example:
```
   export AIRFLOW__CODE_EDITOR__STRING_NORMALIZATION=True
   export AIRFLOW__CODE_EDITOR__MOUNT_NAME='data'
   export AIRFLOW__CODE_EDITOR__MOUNT_PATH=/home/airflow/data
   export AIRFLOW__CODE_EDITOR__MOUNT1_NAME='logs'
   export AIRFLOW__CODE_EDITOR__MOUNT1_PATH=/home/airflow/logs
   export AIRFLOW__CODE_EDITOR__MOUNT2_NAME='tmp'
   export AIRFLOW__CODE_EDITOR__MOUNT2_PATH='/tmp
```

### Development Instructions

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

### Links

* Apache Airflow - https://github.com/apache/airflow
* Codemirror, In-browser code editor - https://github.com/codemirror/codemirror
* Git WebUI, A standalone local web based user interface for git repositories - https://github.com/alberthier/git-webui
* Black, The Uncompromising Code Formatter - https://github.com/psf/black
* Vue.js - https://github.com/vuejs/vue
* Vue-good-table, data table for VueJS - https://github.com/xaksis/vue-good-table
* Vue-tree, TreeView control for VueJS - https://github.com/grapoza/vue-tree
* Splitpanes - https://github.com/antoniandre/splitpanes
* Axios, Promise based HTTP client for the browser and node.js - https://github.com/axios/axios
