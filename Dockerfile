FROM python:alpine

RUN pip install -U pip && pip install flask

WORKDIR /app

CMD flask --app app run

