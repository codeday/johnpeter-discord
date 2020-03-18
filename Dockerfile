FROM python:3.7

COPY requirements.txt /

RUN pip install -r /requirements.txt

COPY cogs/ /app/cogs/
COPY database_classes/ /app/database_classes/
COPY secrets/ /app/secrets/
COPY main.py /app

WORKDIR /app

CMD ["python3", "main.py"]