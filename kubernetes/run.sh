#!/usr/bin/env bash
# disable emojis
export MINIKUBE_IN_STYLE=0

# start a kubernetes cluster
# use the k8s version from GKE
# (1.15.7 is latest as of 2020-01-25)
minikube start --kubernetes-version v1.15.7

# launch the k8s dashboard
minikube dashboard &

# use the minikube docker daemon when building images
eval $(minikube docker-env)
docker build -t pypistats .

# create namespace ``pypistats``
kubectl apply -f kubernetes/minikube/namespace.yaml

# launch the database
kubectl apply -f kubernetes/minikube/database_deployment.yaml --namespace=pypistats
kubectl apply -f kubernetes/minikube/database_service.yaml --namespace=pypistats

# create secret from the env file
#kubectl delete secret pypistats-secrets --namespace=pypistats
kubectl create secret generic pypistats-secrets --from-env-file=envs/minikube.env --namespace=pypistats

# create webserver
kubectl apply -f kubernetes/minikube/web_deployment.yaml --namespace=pypistats
kubectl apply -f kubernetes/minikube/web_service.yaml --namespace=pypistats

# launch the tasks components
kubectl apply -f kubernetes/minikube/tasks_deployment.yaml --namespace=pypistats

# get info about connecting
kubectl cluster-info
kubectl get services --namespace=pypistats
# open the webserver in browser
open "http://$(kubectl cluster-info | grep "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" -o -E -m 1):30500"

