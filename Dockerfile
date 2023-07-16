FROM python:alpine

RUN pip install -U pip && pip install flask

WORKDIR /app

CMD ["./prestart.sh"]

ENTRYPOINT ["python3"]
CMD ["app.py"]
