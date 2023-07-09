FROM python:3.8

RUN mkdir -p /usr/src/core-api
WORKDIR /usr/src/core-api
COPY requirements.txt /usr/src/core-api/

RUN python3 -m pip install -r requirements.txt --no-cache-dir

COPY . /usr/src/core-api

ENTRYPOINT ["sh", "prod_run.sh"]