ARG BUILD_FROM
FROM ${BUILD_FROM}

WORKDIR /app

RUN apk add --no-cache python3 py3-pip

COPY requirements.txt /app/

RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY app.py /app/
COPY run.sh /

RUN chmod +x /run.sh

CMD ["/run.sh"]
