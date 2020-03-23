FROM python:3.7-slim-buster

COPY requirements.txt /

RUN pip install -r /requirements.txt

COPY cogs/ /app/cogs/
COPY database_classes/ /app/database_classes/
COPY main.py /app

COPY service_classes/ /app/service_classes/

WORKDIR /app

CMD ["python3", "main.py"]