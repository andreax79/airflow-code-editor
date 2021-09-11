SHELL=/bin/bash -e

help:
	@echo "- make clean        Clean"
	@echo "- make tag          Create version tag"
	@echo "- make test         Run tests"
	@echo "- make coverage     Run tests coverage"
	@echo "- make lint         Run lint"
	@echo "- make codemirror   Update CodeMirror"
	@echo "- make webserver    Start Airflow webserver"
	@echo "- make scheduler    Start Airflow scheduler"
	@echo "- make npm-build    Run npm build"
	@echo "- make npm-watch    Run npm build when files change"

lint:
	python3 setup.py flake8

tag:
	@grep -q "## $$(cat airflow_code_editor/VERSION)" changelog.txt || (echo "Missing changelog !!! Update changelog.txt"; exit 1)
	@git tag -a "v$$(cat airflow_code_editor/VERSION)" -m "version v$$(cat airflow_code_editor/VERSION)"

webserver:
	@./scripts/airflow.sh webserver

scheduler:
	@./scripts/airflow.sh scheduler

build: clean
	python3 setup.py bdist_wheel
	python3 setup.py sdist bdist_wheel

clean:
	-rm -rf build dist
	-rm -rf *.egg-info

test:
	@./scripts/tests.sh

coverage:
	@./scripts/coverage.sh

codemirror:
	@rm -rf codemirror_src codemirror.zip
	@curl -O https://codemirror.net/codemirror.zip
	@unzip codemirror.zip -d codemirror_src
	@mv codemirror_src/codemirror-*/* codemirror_src
	@rm codemirror.zip
	@cp codemirror_src/lib/codemirror.js airflow_code_editor/static/
	@cp codemirror_src/lib/codemirror.css airflow_code_editor/static/css/
	@cp -a codemirror_src/theme airflow_code_editor/static/css/
	@cp -a codemirror_src/addon airflow_code_editor/static/
	@cp -a codemirror_src/keymap/*.js airflow_code_editor/static/
	@cp -a codemirror_src/mode airflow_code_editor/static/
	@rm -rf codemirror_src
	@python3 update_themes_js.py

npm-build:
	@npm run build

npm-watch:
	@npm run watch
