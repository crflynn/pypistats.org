#!/usr/bin/env bash
set -o allexport
source pypistats/secret/.env
set +o allexport
pipenv run celery beat -A pypistats.run.celery -l info
