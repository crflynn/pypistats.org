#!/usr/bin/env bash

if [[ "$1" = "webdev" ]]
then
  exec poetry run flask run --host 0.0.0.0
fi

if [[ "$1" = "web" ]]
then
  exec poetry run gunicorn -b 0.0.0.0:5000 -w 4 --access-logfile - --error-log - pypistats.run:app
fi

if [[ "$1" = "celery" ]]
then
  exec poetry run celery -A pypistats.run.celery worker -l info
fi

if [[ "$1" = "beat" ]]
then
  exec poetry run celery beat -A pypistats.run.celery -l info
fi

if [[ "$1" = "migrate" ]]
then
  exec poetry run flask db upgrade
fi

if [[ "$1" = "seeds" ]]
then
  exec poetry run python -m migrations.seeds
fi