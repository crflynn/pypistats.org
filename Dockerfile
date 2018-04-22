FROM python:3.6-slim

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD . .

EXPOSE 5000
