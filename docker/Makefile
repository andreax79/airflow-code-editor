IMAGE_NAME := airflow-code-editor
DEV_IMAGE_NAME := ${IMAGE_NAME}-dev
OWNER := andreax79
AIRFLOW_VERSION := 3.0.1
# Must match the Airflow image Python version
DEV_IMAGE_PYTHON_VERSION := 3.12
AIRFLOW_PORT := 8080
PLUGIN_VERSION := $(shell cat ../airflow_code_editor/VERSION)
VERSION := ${AIRFLOW_VERSION}-${PLUGIN_VERSION}
DEV_IMAGE_PACKAGE_DIR := /home/airflow/.local/lib/python${DEV_IMAGE_PYTHON_VERSION}/site-packages/airflow_code_editor/

.PHONY: help banner image push all dev-image dev-shell webserver scheduler test coverage all

makeFileDir := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

help: banner
	@echo "Release:"
	@echo "- make image        Build docker image"
	@echo "- make push         Push docker image"
	@echo "Development image:"
	@echo "- make dev-image    Build dev image"
	@echo "- make dev-shell    Start a shell in the dev environment"
	@echo "- make standalone   Run an all-in-one copy of Airflow"
	@echo "- make api-server   Start a Airflow api-server instance"
	@echo "- make scheduler    Start a scheduler instance"
	@echo "- make tests        Run tests on dev image"
	@echo "- make coverage     Run tests coverage on dev image"


.DEFAULT_GOAL := help

banner:
	@echo "Airflow Version: ${AIRFLOW_VERSION}"
	@echo "Plugin Version:  ${PLUGIN_VERSION}"
	@echo "------------------------------------------"

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
	DOCKER_BUILDKIT=1 docker build \
		 --build-arg AIRFLOW_UID=$$(id -u) \
		 --build-arg PLUGIN_VERSION=${PLUGIN_VERSION} \
		 --build-arg AIRFLOW_VERSION=${AIRFLOW_VERSION} \
		 --tag ${DEV_IMAGE_NAME} \
		 -f Dockerfile.dev \
		 .
	@rm ./requirements.txt ./requirements-optional.txt

dags:
	@git clone https://github.com/andreax79/airflow-maintenance-dags ${makeFileDir}/dags

dev-shell: dags banner
	@touch ${makeFileDir}/.bash_history
	@docker run --rm -it \
		-h airflow \
		-v ${makeFileDir}/.bash_history:/home/airflow/.bash_history \
		-v ${makeFileDir}/dags:/opt/airflow/dags \
		-v ${makeFileDir}/../tests:/opt/airflow/tests \
		-v ${makeFileDir}/../airflow_code_editor:${DEV_IMAGE_PACKAGE_DIR} \
		-v ${makeFileDir}/../sh.py:/opt/airflow/sh.py \
		-p ${AIRFLOW_PORT}:${AIRFLOW_PORT} \
		-e AIRFLOW_UID=$$(id -u) \
		-e AIRFLOW__CODE_EDITOR__ENABLED="True" \
		-e AIRFLOW__CODE_EDITOR__MOUNT="name=airflow_home,path=/opt/airflow" \
		-e AIRFLOW__CODE_EDITOR__MOUNT1="name=logs,path=/opt/airflow/logs" \
		${DEV_IMAGE_NAME} \
		bash -l

webserver:
	@echo Please use `make api-server`.

api-server: dags banner
	@docker run --rm -it \
		-h airflow \
		-v ${makeFileDir}/../airflow_code_editor:${DEV_IMAGE_PACKAGE_DIR} \
		-v ${makeFileDir}/dags:/opt/airflow/dags \
		-v ${makeFileDir}/../tests:/opt/airflow/tests \
		-p ${AIRFLOW_PORT}:${AIRFLOW_PORT} \
		-e AIRFLOW_UID=$$(id -u) \
		-e AIRFLOW__CODE_EDITOR__ENABLED="True" \
		-e AIRFLOW__CODE_EDITOR__MOUNT="name=airflow_home,path=/opt/airflow" \
		-e AIRFLOW__CODE_EDITOR__MOUNT1="name=logs,path=/opt/airflow/logs" \
		${DEV_IMAGE_NAME} \
		airflow api-server

standalone: dags banner
	@docker run --rm -it \
		-h airflow \
		-v ${makeFileDir}/../airflow_code_editor:${DEV_IMAGE_PACKAGE_DIR} \
		-v ${makeFileDir}/dags:/opt/airflow/dags \
		-v ${makeFileDir}/../tests:/opt/airflow/tests \
		-p ${AIRFLOW_PORT}:${AIRFLOW_PORT} \
		-e AIRFLOW_UID=$$(id -u) \
		-e AIRFLOW__CODE_EDITOR__ENABLED="True" \
		-e AIRFLOW__CODE_EDITOR__MOUNT="name=airflow_home,path=/opt/airflow" \
		-e AIRFLOW__CODE_EDITOR__MOUNT1="name=logs,path=/opt/airflow/logs" \
		${DEV_IMAGE_NAME} \
		airflow standalone

scheduler: dags banner
	@docker run --rm -it \
		-h airflow \
		-v ${makeFileDir}/../airflow_code_editor:${DEV_IMAGE_PACKAGE_DIR} \
		-v ${makeFileDir}/dags:/opt/airflow/dags \
		-v ${makeFileDir}/../tests:/opt/airflow/tests \
		-p ${AIRFLOW_PORT}:${AIRFLOW_PORT} \
		-e AIRFLOW_UID=$$(id -u) \
		-e AIRFLOW__CODE_EDITOR__ENABLED="True" \
		-e AIRFLOW__CODE_EDITOR__MOUNT="name=airflow_home,path=/opt/airflow" \
		-e AIRFLOW__CODE_EDITOR__MOUNT1="name=logs,path=/opt/airflow/logs" \
		${DEV_IMAGE_NAME} \
		airflow scheduler

test: dags banner
	@docker run --rm -it \
		-h airflow \
		-v ${makeFileDir}/../airflow_code_editor:${DEV_IMAGE_PACKAGE_DIR} \
		-v ${makeFileDir}/dags:/opt/airflow/dags \
		-v ${makeFileDir}/../tests:/opt/airflow/tests \
		-e AIRFLOW_UID=$$(id -u) \
		-e AIRFLOW__CODE_EDITOR__ENABLED="True" \
		-e AIRFLOW__CODE_EDITOR__MOUNT="name=airflow_home,path=/opt/airflow" \
		-e AIRFLOW__CODE_EDITOR__MOUNT1="name=logs,path=/opt/airflow/logs" \
		--entrypoint pytest \
		${DEV_IMAGE_NAME} \
		tests

coverage: dags banner
	@docker run --rm -it \
		-h airflow \
		-v ${makeFileDir}/../airflow_code_editor:${DEV_IMAGE_PACKAGE_DIR} \
		-v ${makeFileDir}/dags:/opt/airflow/dags \
		-v ${makeFileDir}/../tests:/opt/airflow/tests \
		-e AIRFLOW_UID=$$(id -u) \
		-e AIRFLOW__CODE_EDITOR__ENABLED="True" \
		-e AIRFLOW__CODE_EDITOR__MOUNT="name=airflow_home,path=/opt/airflow" \
		-e AIRFLOW__CODE_EDITOR__MOUNT1="name=logs,path=/opt/airflow/logs" \
		--entrypoint pytest \
		${DEV_IMAGE_NAME} \
		tests \
		--cov=${DEV_IMAGE_PACKAGE_DIR} --cov-report=term-missing

all: help
