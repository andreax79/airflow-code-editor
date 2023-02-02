IMAGE_NAME=airflow-code-editor
OWNER=andreax79
NAMESPACE=airflow
AIRFLOW_VERSION=2.4.1
PLUGIN_VERSION=`cat ../airflow_code_editor/VERSION`
VERSION=${AIRFLOW_VERSION}-${PLUGIN_VERSION}
IMAGE=${OWNER}/${IMAGE_NAME}
NODEPORT=airflow-webserver-nodeport
HELM=helm
KUBECTL=kubectl
WEBSERVER_SECRET_NAME=my-webserver-secret
.PHONY: help up down add_repo create_namespace

help:
	@echo "- make up           Start Airflow"
	@echo "- make down         Stop Airflow"

.DEFAULT_GOAL := help


.webserver_secret_key: create_namespace
	@python3 -c 'import secrets; print(secrets.token_hex(16))' > .webserver_secret_key
	# @openssl rand -hex 16 > .webserver_secret_key
	@${KUBECTL} -n ${NAMESPACE} delete secret generic ${WEBSERVER_SECRET_NAME} 2>/dev/null || true
	@${KUBECTL} -n ${NAMESPACE} create secret generic ${WEBSERVER_SECRET_NAME} --from-file=webserver-secret-key=.webserver_secret_key

create_namespace:
	@${KUBECTL} create namespace ${NAMESPACE} 2>/dev/null || true

add_repo:
	@${HELM} repo add apache-airflow https://airflow.apache.org

up: .webserver_secret_key add_repo
	@${HELM} upgrade --install airflow apache-airflow/airflow \
		--namespace ${NAMESPACE} \
		--create-namespace \
		-f values.yaml \
		--set images.airflow.repository=${IMAGE} \
		--set images.airflow.tag=${VERSION} \
		--debug
	# Expose the Webserver
	@${KUBECTL} --namespace ${NAMESPACE} \
		expose deployment airflow-webserver \
		--type=NodePort \
		--name ${NODEPORT} 2>/dev/null || true
	# Get port
	@${KUBECTL} --namespace ${NAMESPACE} get service ${NODEPORT}

down:
	@${HELM} delete airflow --namespace ${NAMESPACE}

all: help
