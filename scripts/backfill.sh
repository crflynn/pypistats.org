#!/usr/bin/env bash
set -o allexport
source envs/prod.env
set +o allexport
poetry run python -m pypistats.tasks.pypi
