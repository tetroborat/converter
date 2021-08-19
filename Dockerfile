FROM python:3.7

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /server_test

COPY ./rq.txt /rq.txt
RUN pip install -r /rq.txt

COPY . /server_test
