#!/usr/bin/env bash
docker build -t us.gcr.io/pypistats-org/pypistats:$(poetry version | tail -c +14) .
docker push us.gcr.io/pypistats-org/pypistats:$(poetry version | tail -c +14)

kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0/aio/deploy/recommended.yaml

# create namespace ``pypistats``
kubectl apply -f kubernetes/namespace.yaml

# create secret from the env file
#kubectl delete secret pypistats-secrets --namespace=pypistats
# create
kubectl create secret generic pypistats-secrets --from-env-file=gke.env --namespace=pypistats
# update
kubectl create secret generic pypistats-secrets --from-env-file=gke.env --namespace=pypistats --dry-run -o yaml | kubectl apply -f -

# create redis and flower
kubectl apply -f kubernetes/redis.yaml --namespace=pypistats
kubectl apply -f kubernetes/flower.yaml --namespace=pypistats

# launch the web components
kubectl apply -f kubernetes/web.yaml --namespace=pypistats

# launch the tasks components
kubectl apply -f kubernetes/tasks.yaml --namespace=pypistats

# get info about connecting
kubectl cluster-info
kubectl get services --namespace=pypistats

