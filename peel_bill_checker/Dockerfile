ARG BUILD_FROM
FROM ${BUILD_FROM}

WORKDIR /app

RUN apk add --no-cache python3 py3-pip

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY app.py .

COPY run.sh /run.sh

RUN chmod +x /run.sh

CMD ["/run.sh"]
