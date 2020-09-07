# Airflow Code Editor Plugin
A plugin for [Apache Airflow](https://github.com/apache/airflow) that allows you to edit DAGs in browser.
The DAGs are stored in a Git repository. You may use it to view Git history, review local changes and commit.

### System Requirements

* Airflow Versions
    * 1.10.3 or newer
* git Versions
    * 2.0 or newer

### Screenshots

![Code editor](https://andreax79.github.io/airflow-code-editor/screenshots/2.png)

![Git diff](https://andreax79.github.io/airflow-code-editor/screenshots/1.png)


### Deployment Instructions

1. Install the plugin

    pip install airflow-code-editor

2. Restart the Airflow Web Server

3. Open Admin - DAGs Code Editor


### Config Options

You can edit your *airflow.cfg* adding any of the following settings in the \[code_editor\] section.

* **git_cmd**  git command (optional path)
* **git_default_args**  git arguments added to each call (default: -c color.ui=true)
* **git_author_name** human-readable name in the author/committer (default logged user first and last names)
* **git_author_email** email for the author/committer (default: logged user email)
* **git_init_repo**  initialize a git repo in DAGs folder (default: True)
* **root_folder**  root folder (default: Airflow DAGs folder)
* **mount_name**  configure additional file folder name (mount point)
* **mount_path**  configure additional file path

Example:
```
   [code_editor]
   git_cmd = /usr/bin/git
   git_default_args = -c color.ui=true
   git_init_repo = False
   root_folder = /home/airflow/dags
   mount_name = data
   mount_path = /home/airflow/data
   mount1_name = logs
   mount1_path = /home/airflow/logs
```

### Links

* Apache Airflow - https://github.com/apache/airflow
* Codemirror, In-browser code editor - https://github.com/codemirror/codemirror
* Git WebUI, A standalone local web based user interface for git repositories - https://github.com/alberthier/git-webui

