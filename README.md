# Airflow Code Editor Plugin

This plugin for [Apache Airflow](https://github.com/apache/airflow) allows you to edit DAGs directly within your browser,
providing a seamless and efficient workflow for managing your pipelines.
Offering a user-friendly file management interface within designated directories, it facilitates effortless editing,
uploading, and downloading of files.
With Git support enabled, DAGs are stored in a Git repository, enabling users to explore Git history, review local modifications, and commit changes.

[![Build Status](https://github.com/andreax79/airflow-code-editor/workflows/Tests/badge.svg)](https://github.com/andreax79/airflow-code-editor/actions)
[![PyPI version](https://badge.fury.io/py/airflow-code-editor.svg)](https://badge.fury.io/py/airflow-code-editor)
[![PyPI](https://img.shields.io/pypi/pyversions/airflow-code-editor.svg)](https://pypi.org/project/airflow-code-editor)
[![Downloads](https://static.pepy.tech/badge/airflow-code-editor/month)](https://pepy.tech/project/airflow-code-editor)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

### System Requirements

* Airflow Versions
    * 1.10.3 or newer
* git Versions (git is not required if git support is disabled)
    * 2.0 or newer

### Screenshots

#### File Manager

![File Manager](https://github.com/andreax79/airflow-code-editor/assets/1288154/6d9b09df-4503-45d9-94d4-ff013a86985a)

#### Editor

![Editor](https://github.com/andreax79/airflow-code-editor/assets/1288154/4ffaed29-390f-4134-bcb4-0b8fb8c59060)

#### Search

![Search](https://github.com/andreax79/airflow-code-editor/assets/1288154/9ba81166-3823-40ae-8820-116e4e5d2588)

#### Git History

![Git History](https://github.com/andreax79/airflow-code-editor/assets/1288154/2d6ec31f-3c1c-4d38-8fc6-99d18096cc64)

#### Git Workspace

![Git Workspace](https://github.com/andreax79/airflow-code-editor/assets/1288154/eb041a02-3f1e-47a1-b179-072d66e4662d)


### Install Instructions

#### Docker Images

For the ease of deployment, use the production-ready reference container image.
The image is based on the reference images for Apache Airflow.

You can find the following images there:
* andreax79/airflow-code-editor:**latest** - the latest released Airflow Code Editor image with the latest Apache Airflow version
* andreax79/airflow-code-editor:**2.10.0** - the latest released Airflow Code Editor with specific Airflow version
* andreax79/airflow-code-editor:**2.10.0-7.7.0** - specific version of Airflow and Airflow Code Editor

#### Installing from PyPI

1. Install the plugin

  ```bash
    pip install airflow-code-editor
  ```

2. Install optional dependencies

* black - Black Python code formatter
* isort - A Python utility/library to sort imports
* fs-s3fs - S3FS Amazon S3 Filesystem
* fs-gcsfs - Google Cloud Storage Filesystem
* ... other filesystems supported by PyFilesystem - see https://www.pyfilesystem.org/page/index-of-filesystems/

  ```bash
    pip install black isort fs-s3fs fs-gcsfs
  ```

3. Restart the Airflow Web Server

4. Open Admin - DAGs Code Editor


### Config Options

You can set options editing the Airflow's configuration file or setting environment variables.
You can edit your *airflow.cfg* adding any of the following settings in the \[code_editor\] section.
All the settings are optional.

* **enabled**  enable this plugin (default: True).
* **git_enabled**  enable git support (default: True). If git is not installed, disable this option.
* **git_cmd**  git command (path)
* **git_default_args**  git arguments added to each call (default: -c color.ui=true)
* **git_author_name** human-readable name in the author/committer (default logged user first and last names)
* **git_author_email** email for the author/committer (default: logged user email)
* **git_init_repo**  initialize a git repo in DAGs folder (default: True)
* **root_directory**  root folder (default: Airflow DAGs folder)
* **line_length**  Python code formatter - max line length (default: 88)
* **string_normalization**  Python code formatter - if true normalize string quotes and prefixes (default: False)
* **mount**, **mount1**, ...  configure additional folder (mount point) - format: name=xxx,path=yyy
* **ignored_entries** comma-separated list of entries to be excluded from file/directory list (default: .\*,\_\_pycache\_\_)

```
   [code_editor]
   enabled = True
   git_enabled = True
   git_cmd = /usr/bin/git
   git_default_args = -c color.ui=true
   git_init_repo = False
   root_directory = /home/airflow/dags
   line_length = 88
   string_normalization = False
   mount = name=data,path=/home/airflow/data
   mount1 = name=logs,path=/home/airflow/logs
   mount2 = name=data,path=s3://example
```

Mount Options:

* **name**: mount name (destination)
* **path**: local path or PyFilesystem FS URLs - see https://docs.pyfilesystem.org/en/latest/openers.html

Example:
* name=ftp_server,path=ftp://user:pass@ftp.example.org/private
* name=data,path=s3://example
* name=tmp,path=/tmp

You can also set options with the following environment variables:

* AIRFLOW__CODE_EDITOR__ENABLED
* AIRFLOW__CODE_EDITOR__GIT_ENABLED
* AIRFLOW__CODE_EDITOR__GIT_CMD
* AIRFLOW__CODE_EDITOR__GIT_DEFAULT_ARGS
* AIRFLOW__CODE_EDITOR__GIT_AUTHOR_NAME
* AIRFLOW__CODE_EDITOR__GIT_AUTHOR_EMAIL
* AIRFLOW__CODE_EDITOR__GIT_INIT_REPO
* AIRFLOW__CODE_EDITOR__ROOT_DIRECTORY
* AIRFLOW__CODE_EDITOR__LINE_LENGTH
* AIRFLOW__CODE_EDITOR__STRING_NORMALIZATION
* AIRFLOW__CODE_EDITOR__MOUNT, AIRFLOW__CODE_EDITOR__MOUNT1, AIRFLOW__CODE_EDITOR__MOUNT2, ...
* AIRFLOW__CODE_EDITOR__IGNORED_ENTRIES

Example:
```
   export AIRFLOW__CODE_EDITOR__STRING_NORMALIZATION=True
   export AIRFLOW__CODE_EDITOR__MOUNT='name=data,path=/home/airflow/data'
   export AIRFLOW__CODE_EDITOR__MOUNT1='name=logs,path=/home/airflow/logs'
   export AIRFLOW__CODE_EDITOR__MOUNT2='name=tmp,path=/tmp'
```

### REST API

Airflow Code Editor provides a REST API. Through this API, users can interact with the application
programmatically, enabling automation, data retrieval, and integration with other software.

For detailed information on how to use each endpoint, refer to the
[API documentation](https://petstore.swagger.io/?url=https://raw.githubusercontent.com/andreax79/airflow-code-editor/main/airflow_code_editor/api/code_editor.yaml).

### REST API Authentication

The API authentication is inherited from the Apache Airflow.

If you want to check which auth backend is currently set, you can use
`airflow config get-value api auth_backends` command as in the example below.
```bash
$ airflow config get-value api auth_backends
airflow.api.auth.backend.basic_auth
```

For details on configuring the authentication, see
[API Authorization](https://airflow.apache.org/docs/apache-airflow/stable/security/api.html).

### Development Instructions

1. Fork the repo

2. Clone it on the local machine

  ```bash
    git clone https://github.com/andreax79/airflow-code-editor.git
    cd airflow-code-editor
  ```

3. Create dev image

  ```bash
    make dev-image
  ```

4. Switch node version

  ```bash
    nvm use
  ```

5. Make changes you need. Build npm package with:

  ```bash
    make npm-build
  ```

6. You can start Airflow webserver with:

  ```bash
    make webserver
  ```

7. Run tests

  ```bash
    make test
  ```

8. Commit and push changes

9. Create [pull request](https://github.com/andreax79/airflow-code-editor/compare) to the original repo

### Links

* [Apache Airflow](https://github.com/apache/airflow)
* [Codemirror, In-browser code editor](https://github.com/codemirror/codemirror)
* [codemirror-theme-bundle, custom themes for CodeMirror 6](https://github.com/fsegurai/codemirror-themes)
* [codemirror-vim, Vim keybindings for CodeMirror 6](https://github.com/replit/codemirror-vim)
* [codemirror-emacs, Emacs keybindings for CodeMirror 6](https://github.com/replit/codemirror-emacs)
* [Git WebUI, A standalone local web based user interface for git repositories](https://github.com/alberthier/git-webui)
* [Black, The Uncompromising Code Formatter](https://github.com/psf/black)
* [isort, A Python utility/library to sort imports](https://github.com/psf/black)
* [pss, power-tool for searching source files](https://github.com/eliben/pss)
* [Vue.js](https://github.com/vuejs/vue)
* [Vue-good-table, data table for VueJS](https://github.com/xaksis/vue-good-table)
* [Vue-tree, TreeView control for VueJS](https://github.com/grapoza/vue-tree)
* [Vue-universal-modal Universal modal plugin for Vue@3](https://github.com/hoiheart/vue-universal-modal)
* [Vue-simple-context-menu](https://github.com/johndatserakis/vue-simple-context-menu)
* [vue3-notification, Vue.js notifications](https://github.com/kyvg/vue3-notification)
* [Splitpanes](https://github.com/antoniandre/splitpanes)
* [Axios, Promise based HTTP client for the browser and node.js](https://github.com/axios/axios)
* [PyFilesystem2, Python's Filesystem abstraction layer](https://github.com/PyFilesystem/pyfilesystem2)
* [Amazon S3 PyFilesystem](https://github.com/PyFilesystem/s3fs)
* [Google Cloud Storage PyFilesystem](https://github.com/Othoz/gcsfs)
