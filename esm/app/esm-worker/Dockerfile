FROM openfold

COPY requirements.txt /opt/openfold/

RUN python3 -m pip install -r requirements.txt --no-cache-dir

COPY . /opt/openfold/

ENTRYPOINT ["sh", "prod_run.sh"]