IMAGE_NAME=airflow-code-editor
DEV_IMAGE_NAME=${IMAGE_NAME}-dev
OWNER=andreax79
AIRFLOW_VERSION=2.6.1
AIRFLOW_PORT=8080
PLUGIN_VERSION=`cat ../airflow_code_editor/VERSION`
VERSION=${AIRFLOW_VERSION}-${PLUGIN_VERSION}

.PHONY: help build test format image push all

help:
	@echo "Release:"
	@echo "- make image        Build docker image"
	@echo "- make push         Push docker image"
	@echo "Development:"
	@echo "- make dev-image    Build dev image"
	@echo "- make dev-shell    Start a shell in the dev environment"
	@echo "- make webserver    Start Airflow webserver from dev image"

.DEFAULT_GOAL := help

image:
	@cp  ../requirements-optional.txt .
	@DOCKER_BUILDKIT=1 docker build \
		 --build-arg PLUGIN_VERSION=${PLUGIN_VERSION} \
		 --build-arg AIRFLOW_VERSION=${AIRFLOW_VERSION} \
		 --tag ${IMAGE_NAME}:latest \
		 --tag ${IMAGE_NAME}:${AIRFLOW_VERSION} \
		 --tag ${IMAGE_NAME}:${VERSION} \
		 .
	@rm ./requirements-optional.txt

push:
	@docker tag ${IMAGE_NAME}:${VERSION} ghcr.io/${OWNER}/${IMAGE_NAME}:${VERSION}
	@docker tag ${IMAGE_NAME}:${VERSION} ghcr.io/${OWNER}/${IMAGE_NAME}:${AIRFLOW_VERSION}
	@docker tag ${IMAGE_NAME}:${VERSION} ghcr.io/${OWNER}/${IMAGE_NAME}:latest
	@docker push ghcr.io/${OWNER}/${IMAGE_NAME}:${VERSION}
	@docker push ghcr.io/${OWNER}/${IMAGE_NAME}:${AIRFLOW_VERSION}
	@docker push ghcr.io/${OWNER}/${IMAGE_NAME}:latest
	@docker tag ${IMAGE_NAME}:${VERSION} ${OWNER}/${IMAGE_NAME}:${VERSION}
	@docker tag ${IMAGE_NAME}:${VERSION} ${OWNER}/${IMAGE_NAME}:${AIRFLOW_VERSION}
	@docker tag ${IMAGE_NAME}:${VERSION} ${OWNER}/${IMAGE_NAME}:latest
	@docker push ${OWNER}/${IMAGE_NAME}:${VERSION}
	@docker push ${OWNER}/${IMAGE_NAME}:${AIRFLOW_VERSION}
	@docker push ${OWNER}/${IMAGE_NAME}:latest

push-version:
	@echo ${AIRFLOW_VERSION}
	# @cp ../requirements-optional.txt .
	# @DOCKER_BUILDKIT=1 docker build \
	# 	 --build-arg PLUGIN_VERSION=${PLUGIN_VERSION} \
	# 	 --build-arg AIRFLOW_VERSION=${AIRFLOW_VERSION} \
	# 	 --tag ${IMAGE_NAME}:${VERSION} \
	# 	 --tag ${IMAGE_NAME}:${AIRFLOW_VERSION} \
	# 	 .
	# @rm ./requirements-optional.txt
	@docker tag ${IMAGE_NAME}:${VERSION} ghcr.io/${OWNER}/${IMAGE_NAME}:${VERSION}
	@docker tag ${IMAGE_NAME}:${VERSION} ghcr.io/${OWNER}/${IMAGE_NAME}:${AIRFLOW_VERSION}
	@docker push ghcr.io/${OWNER}/${IMAGE_NAME}:${VERSION}
	@docker push ghcr.io/${OWNER}/${IMAGE_NAME}:${AIRFLOW_VERSION}
	@docker tag ${IMAGE_NAME}:${VERSION} ${OWNER}/${IMAGE_NAME}:${VERSION}
	@docker tag ${IMAGE_NAME}:${VERSION} ${OWNER}/${IMAGE_NAME}:${AIRFLOW_VERSION}
	@docker push ${OWNER}/${IMAGE_NAME}:${VERSION}
	@docker push ${OWNER}/${IMAGE_NAME}:${AIRFLOW_VERSION}

dev-image:
	@cp ../requirements.txt ../requirements-optional.txt .
	@DOCKER_BUILDKIT=1 docker build \
		 --build-arg=AIRFLOW_UID=$$(id -u) \
		 --build-arg PLUGIN_VERSION=${PLUGIN_VERSION} \
		 --build-arg AIRFLOW_VERSION=${AIRFLOW_VERSION} \
		 --tag ${DEV_IMAGE_NAME} \
		 -f Dockerfile.dev \
		 .
	@rm ./requirements.txt ./requirements-optional.txt

dags:
	@git clone https://github.com/andreax79/airflow-maintenance-dags dags

dev-shell:
	@touch ${PWD}/.bash_history
	@docker run --rm -it \
		-h airflow \
		-v ${PWD}/.bash_history:/home/airflow/.bash_history \
		-v ${PWD}/dags:/opt/airflow/dags \
		-v ${PWD}/../airflow_code_editor:/home/airflow/.local/lib/python3.7/site-packages/airflow_code_editor/ \
		-p ${AIRFLOW_PORT}:${AIRFLOW_PORT} \
		-e AIRFLOW_UID=$$(id -u) \
		${DEV_IMAGE_NAME} \
		bash -l

webserver:
	@docker run --rm -it \
		-h airflow \
		-v ${PWD}/../airflow_code_editor:/home/airflow/.local/lib/python3.7/site-packages/airflow_code_editor/ \
		-v ${PWD}/dags:/opt/airflow/dags \
		-p ${AIRFLOW_PORT}:${AIRFLOW_PORT} \
		-e AIRFLOW_UID=$$(id -u) \
		${DEV_IMAGE_NAME} \
		airflow webserver

all: help