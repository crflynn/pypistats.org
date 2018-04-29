FROM python:3.6-slim
RUN apt-get update && apt-get install -y supervisor redis-server
RUN pip install pipenv

ENV WORKON_HOME=/venv

WORKDIR /app

ADD Pipfile /app
ADD Pipfile.lock /app

RUN pipenv install --verbose

ADD . /app

EXPOSE 5000

ENV C_FORCE_ROOT=1


CMD /usr/bin/supervisord
