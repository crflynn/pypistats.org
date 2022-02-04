#!/usr/bin/env bash

if [[ "$1" = "webdev" ]]
then
  exec poetry run flask run --host 0.0.0.0
fi

if [[ "$1" = "web" ]]
then
  exec poetry run gunicorn -b 0.0.0.0:5000 -w 2 --access-logfile - --error-log - --access-logformat "%({x-forwarded-for}i)s %(l)s %(h)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\"" pypistats.run:app
fi

if [[ "$1" = "celery" ]]
then
  exec poetry run celery -A pypistats.extensions.celery worker -l info --concurrency=1
fi

if [[ "$1" = "beat" ]]
then
  exec poetry run celery -A pypistats.extensions.celery beat -l info
fi

if [[ "$1" = "flower" ]]
then
  exec poetry run flower -A pypistats.extensions.celery -l info
fi

if [[ "$1" = "migrate" ]]
then
  exec poetry run flask db upgrade
fi

if [[ "$1" = "seeds" ]]
then
  exec poetry run python -m migrations.seeds
fi