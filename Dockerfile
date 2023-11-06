FROM python:3.11.6-bookworm

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

ENTRYPOINT /bin/bash
