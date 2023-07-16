FROM python:alpine

RUN pip install -U pip && pip install flask

WORKDIR /app

ENTRYPOINT ["./prestart.sh"]
