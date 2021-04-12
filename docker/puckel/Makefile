SHELL=/bin/bash -e

help:
	@echo - make build
	@echo - make clean
	@echo - make run

build:
	docker build -t 'test:Dockerfile' .

clean:
	docker rmi 'test:Dockerfile'

run:
	docker run --rm -p 8080:8080 -it test:Dockerfile
