FROM python:3.6-slim
RUN apt-get update && apt-get install -y supervisor redis-server

WORKDIR /app

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

ADD . /app

EXPOSE 5000

ENV C_FORCE_ROOT=1

CMD /usr/bin/supervisord
