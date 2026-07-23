ARG BUILD_FROM
FROM ${BUILD_FROM}

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip3 install --no-cache-dir -r /app/requirements.txt

COPY app.py /app/app.py

COPY run.sh /run.sh

RUN chmod 755 /run.sh

CMD ["/run.sh"]
