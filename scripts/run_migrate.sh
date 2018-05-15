export ENV=prod
set -o allexport
source pypistats/secret/$ENV.env
set +o allexport
# flask db revision --message "message" --autogenerate
# flask db upgrade
