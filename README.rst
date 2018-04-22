PyPI Stats
==========

A simple analytics dashboard for aggregate data on PyPI downloads. PyPI Stats
is built using Flask with plotly.js and deployed to AWS using Zappa.

`PyPI Stats <https://pypistats.org/>`_

Commands
--------
Beat:

pipenv run celery beat -A pypistats.run.celery --loglevel=INFO

Celery worker:

pipenv run celery -A pypistats.run.celery worker --loglevel=INFO
