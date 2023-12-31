FROM python:latest

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# RUN apt-get update && apt-get install -y build-essentials

RUN pip install flask celery redis==4.5.2

WORKDIR /app