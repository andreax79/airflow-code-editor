# Deploying Airflow Code Editor on Kubernetes

Steps to run Airflow Code Editoron a Kubernetes cluster using helm.

## Installation steps

Add Airflow chart repository:
```bash
$ helm repo add apache-airflow https://airflow.apache.org
"apache-airflow" has been added to your repositories
```

Create the namespace:
```bash
$ kubectl create namespace airflow
namespace/airflow created
```

Generate the Fernet key:

```bash
# Python
$ python3 -c 'import secrets; print(secrets.token_hex(16))' > .webserver_secret_key
# or OpenSSL
$ openssl rand -hex 16 > .webserver_secret_key
$ kubectl -n airflow create secret generic my-webserver-secret --from-file=webserver-secret-key=.webserver_secret_key
secret/my-webserver-secret created
```

Install Airflow + Airflow Code Editor:
```bash
$ helm upgrade --install airflow apache-airflow/airflow \
    --namespace airflow \
    --create-namespace \
    -f values.yaml \
    --set images.airflow.repository=andreax79/airflow-code-editor \
    --set images.airflow.tag=2.4.1-7.2.1
Release "airflow" does not exist. Installing it now.
NAME: airflow
LAST DEPLOYED: Mon Jan 30 09:46:09 2023
NAMESPACE: airflow
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
Thank you for installing Apache Airflow 2.4.1!

Your release is named airflow.
You can now access your dashboard(s) by executing the following command(s) and visiting the corresponding port at localhost in your browser:

Airflow Webserver:     kubectl port-forward svc/airflow-webserver 8080:8080 --namespace airflow
Default Webserver (Airflow UI) Login credentials:
    username: admin
    password: admin
Default Postgres connection credentials:
    username: postgres
    password: postgres
    port: 5432

You can get Fernet Key value by running the following:

    echo Fernet Key: $(kubectl get secret --namespace airflow airflow-fernet-key -o jsonpath="{.data.fernet-key}" | base64 --decode)
```

Expose the Webserver:
```bash
$ kubectl --namespace airflow expose deployment airflow-webserver --type=NodePort --name airflow-webserver-nodeport
service/airflow-webserver-nodeport exposed
```

Get port:
```bash
$ kubectl --namespace airflow get service | grep NodePort
airflow-webserver-nodeport    NodePort    10.152.183.185   <none>        8080:30383/TCP      29s
```

Check if Airflow is running:
```bash
$ kubectl get pods -n airflow
```

Uninstall
```bash
$ helm delete airflow --namespace airflow
$ kubectl delete namespace airflow
```

### Links

* [Airflow Helm Chart](https://github.com/airflow-helm/charts/tree/main/charts/airflow)
