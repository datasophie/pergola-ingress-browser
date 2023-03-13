FROM python:3.11-slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /pergola

COPY LICENSE LICENSE
COPY app app
COPY main.py main.py

ENV PYTHONUNBUFFERED="True"
ENV FLASK_APP=app
CMD flask run --host=0.0.0.0 --port 5050
