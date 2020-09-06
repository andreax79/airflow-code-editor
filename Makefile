SHELL=/bin/bash -e

help:
	@echo - make release
	@echo - make lint
	@echo - make clean
	@echo - make test

lint:
	python3 setup.py flake8

release:
	rm -rf dist
	python3 setup.py sdist bdist_wheel
	python3 setup.py bdist_wheel
	twine upload -r pypi dist/*

clean:
	-rm -rf build dist
	-rm -rf *.egg-info

test:
	@nosetests
