# Dockerfile
FROM python:3.10-alpine3.19

RUN apk add bash

WORKDIR /app

COPY . .

RUN pip install .

ENTRYPOINT ["urlshortener"]