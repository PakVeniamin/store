FROM python:3.11.2-alpine

COPY requirements.txt /temp/requirements.txt
RUN apk add postgresql-client build-base postgresql-dev

RUN pip install -r /temp/requirements.txt

COPY store_server /store_server
WORKDIR /store_server
EXPOSE 8000

RUN adduser --disabled-password store-user

USER store-user
