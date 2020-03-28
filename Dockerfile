FROM python:3.7-slim-buster

COPY requirements.txt /

RUN pip install -r /requirements.txt

COPY cogs/ /app/cogs/
COPY database/ /app/database/
COPY services/ /app/services/
COPY main.py /app

WORKDIR /app

CMD ["python3", "main.py"]
