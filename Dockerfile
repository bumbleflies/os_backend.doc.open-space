FROM python:alpine

RUN pip install -U pip

WORKDIR /app

EXPOSE 5000

CMD ./prestart.sh;python app.py
