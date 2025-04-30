SHELL=/bin/bash -e

help:
	@echo "- make clean        Clean"
	@echo "- make tag          Create version tag"
	@echo "- make test         Run tests"
	@echo "- make coverage     Run tests coverage"
	@echo "- make lint         Run lint"
	@echo "- make npm-build    Run npm build"
	@echo "- make npm-watch    Run npm build when files change"
	@echo "Development image:"
	@echo "- make dev-image    Build dev image"
	@echo "- make dev-shell    Start a shell in the dev environment"
	@echo "- make standalone   Run an all-in-one copy of Airflow"
	@echo "- make api-server   Start a Airflow api-server instance"
	@echo "- make scheduler    Start a scheduler instance"

lint:
	flake8 airflow_code_editor tests

isort:
	isort --profile black airflow_code_editor tests

black: isort
	black -S airflow_code_editor tests

tag:
	@grep -q "[$$(cat airflow_code_editor/VERSION)]" changelog.txt || (echo "Missing changelog !!! Update changelog.txt"; exit 1)
	@git tag -a "v$$(cat airflow_code_editor/VERSION)" -m "version v$$(cat airflow_code_editor/VERSION)"

dev-image:
	$(MAKE) -C docker dev-image

dev-shell:
	$(MAKE) -C docker dev-shell

webserver:
	$(MAKE) -C docker webserver

scheduler:
	$(MAKE) -C docker scheduler

api-server:
	$(MAKE) -C docker api-server

build: clean
	python3 setup.py bdist_wheel
	python3 setup.py sdist bdist_wheel

clean:
	-rm -rf build dist
	-rm -rf *.egg-info

test:
	$(MAKE) -C docker test

coverage:
	$(MAKE) -C docker coverage

npm-build:
	@npm run build

npm-watch:
	@npm run watch
