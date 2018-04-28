export ENV=prod
set -o allexport
source pypistats/secret/$ENV.env
set +o allexport
pipenv run flask run --host=0.0.0.0
