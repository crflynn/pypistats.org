export ENV=prod
set -o allexport
source pypistats/secret/$ENV.env
set +o allexport
# pipenv run flask run --host=0.0.0.0
pipenv run gunicorn -b 0.0.0.0:5000 -w 4 --access-logfile - --error-log - pypistats.run:app
