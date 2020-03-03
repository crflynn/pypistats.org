#!/usr/bin/env bash
set -o allexport
source pypistats/secret/.env
set +o allexport
#pipenv run flask run --host=0.0.0.0
pipenv run gunicorn -b 0.0.0.0:5000 -w 4 --access-logfile - --error-log - --access-logformat "%({x-forwarded-for}i)s %(h)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\"" pypistats.run:app
