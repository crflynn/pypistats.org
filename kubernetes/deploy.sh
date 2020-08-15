#!/usr/bin/env bash
poetry version major
export PYPISTATS_VERSION=$(poetry version | tail -c +14)
docker build -t us.gcr.io/pypistats-org/pypistats:${PYPISTATS_VERSION} .
docker push us.gcr.io/pypistats-org/pypistats:${PYPISTATS_VERSION}
kubectl create secret generic pypistats-secrets --from-env-file=gke.env --namespace=pypistats --dry-run -o yaml | kubectl apply -f -
sed -i '.bak' 's|us.gcr.io\/pypistats-org\/pypistats.*|us.gcr.io\/pypistats-org\/pypistats:'"$PYPISTATS_VERSION"'|g' kubernetes/*.yaml
rm kubernetes/*.bak
kubectl apply -f kubernetes/redis.yaml --namespace=pypistats
kubectl apply -f kubernetes/tasks.yaml --namespace=pypistats
kubectl apply -f kubernetes/flower.yaml --namespace=pypistats
kubectl apply -f kubernetes/web.yaml --namespace=pypistats
