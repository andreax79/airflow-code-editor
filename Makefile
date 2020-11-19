SHELL=/bin/bash -e

help:
	@echo - make release
	@echo - make lint
	@echo - make clean
	@echo - make test
	@echo - make codemirror
	@echo - make webserver

lint:
	python3 setup.py flake8

release: build
	twine upload -r pypi dist/*

webserver: build
	./test_virtualenv/airflow.sh webserver

build: clean
	python3 setup.py bdist_wheel
	python3 setup.py sdist bdist_wheel

clean:
	-rm -rf build dist
	-rm -rf *.egg-info

test:
	@nosetests

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
