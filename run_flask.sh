export ENV=prod
set -o allexport
source pypistats/secret/$ENV.env
set +o allexport
# python -m pypistats.tasks.pypi
flask run --host=0.0.0.0
