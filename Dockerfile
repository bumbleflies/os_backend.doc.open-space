FROM python:alpine

RUN pip install -U pip && pip install flask

WORKDIR /app

CMD ./prestart.sh;python app.py
