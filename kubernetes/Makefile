NAMESPACE=airflow
SSH_KEY=ssh-keys/id_rsa
WEB_SERVER_SECRET_KEY=.webserver_secret_key

.PHONY: help
help:
	@LC_ALL=C $(MAKE) -npq : 2> /dev/null | awk -v RS= -F: '$$1 ~ /^[^.#%]+$$/ { print "- " $$1 }' | sort

$(SSH_KEY):
	mkdir -p ssh-keys
	ssh-keygen -t rsa -b 4096 -f $(SSH_KEY) -N ""

$(WEB_SERVER_SECRET_KEY):
	@python3 -c 'import secrets; print(secrets.token_hex(16))' > .webserver_secret_key
	# @openssl rand -hex 16 > .webserver_secret_key

setup: $(SSH_KEY) $(WEB_SERVER_SECRET_KEY)
	kubectl get namespace | grep -q "^${NAMESPACE} " || kubectl create namespace ${NAMESPACE}
	# helm repo add apache-airflow https://airflow.apache.org
	kubectl delete secret ssh-keys -n "${NAMESPACE}" 2>/dev/null || true
	kubectl create secret generic ssh-keys -n "${NAMESPACE}" \
	  --from-file=id_rsa=./ssh-keys/id_rsa \
	  --from-file=id_rsa.pub=./ssh-keys/id_rsa.pub
	kubectl delete secret generic webserver-secret -n ${NAMESPACE}  2>/dev/null || true
	kubectl create secret generic webserver-secret --from-file=webserver-secret-key=${WEB_SERVER_SECRET_KEY} -n ${NAMESPACE}

up:
	helm upgrade --install airflow apache-airflow/airflow --namespace "${NAMESPACE}" -f values.yaml

down:
	helm uninstall airflow
