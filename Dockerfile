FROM python:3

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app
RUN pip install -U pip

ADD requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
