FROM python:3.6-slim
RUN apt-get update && apt-get install -y supervisor redis-server
RUN pip install pipenv==2018.10.13

ENV WORKON_HOME=/venv
ENV C_FORCE_ROOT="true"

WORKDIR /app

ADD Pipfile /app
ADD Pipfile.lock /app

RUN pipenv install

ADD . /app

EXPOSE 5000


CMD /usr/bin/supervisord
