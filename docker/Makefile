IMAGE_NAME=airflow-code-editor
OWNER=andreax79
AIRFLOW_VERSION=2.5.2
PLUGIN_VERSION=`cat ../airflow_code_editor/VERSION`
VERSION=${AIRFLOW_VERSION}-${PLUGIN_VERSION}

.PHONY: help build test format image push all

help:
	@echo "- make image        Build docker image"
	@echo "- make push         Push docker image"

.DEFAULT_GOAL := help

image:
	@cp ../requirements-optional.txt .
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

all: help
