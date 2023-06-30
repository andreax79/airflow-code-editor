SHELL=/bin/bash -e

help:
	@echo "- make clean        Clean"
	@echo "- make tag          Create version tag"
	@echo "- make test         Run tests"
	@echo "- make coverage     Run tests coverage"
	@echo "- make lint         Run lint"
	@echo "- make codemirror   Update CodeMirror"
	@echo "- make npm-build    Run npm build"
	@echo "- make npm-watch    Run npm build when files change"
	@echo "Development image:"
	@echo "- make dev-image    Build dev image"
	@echo "- make dev-shell    Start a shell in the dev environment"
	@echo "- make standalone   Run an all-in-one copy of Airflow"
	@echo "- make webserver    Start a Airflow webserver instance"
	@echo "- make scheduler    Start a scheduler instance"

lint:
	flake8 airflow_code_editor tests

black:
	black -S airflow_code_editor tests

tag:
	@grep -q "## $$(cat airflow_code_editor/VERSION)" changelog.txt || (echo "Missing changelog !!! Update changelog.txt"; exit 1)
	@git tag -a "v$$(cat airflow_code_editor/VERSION)" -m "version v$$(cat airflow_code_editor/VERSION)"

dev-image:
	$(MAKE) -C docker dev-image

dev-shell:
	$(MAKE) -C docker dev-shell

webserver:
	$(MAKE) -C docker webserver

scheduler:
	$(MAKE) -C docker scheduler

standalone:
	$(MAKE) -C docker standalone

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
	@curl -O https://codemirror.net/5/codemirror.zip
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
