ARG BUILD_FROM
FROM ${BUILD_FROM}

WORKDIR /app

COPY requirements.txt /app/

RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY app.py /app/

COPY run.sh /

RUN chmod +x /run.sh

CMD ["/run.sh"]
