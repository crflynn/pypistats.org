#!/usr/bin/env bash
set -o allexport
source pypistats/secret/.env
set +o allexport
pipenv run python -m pypistats.tasks.pypi
