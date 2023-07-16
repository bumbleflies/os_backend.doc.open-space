FROM python:alpine

RUN pip install -U pip && pip install flask

WORKDIR /app

EXPOSE 5000

CMD ./prestart.sh;python app.py
