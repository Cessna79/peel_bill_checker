ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest

FROM ${BUILD_FROM}

WORKDIR /app

COPY app.py /app/app.py
COPY run.sh /app/run.sh
COPY requirements.txt /app/requirements.txt

RUN chmod +x /app/run.sh

RUN pip3 install --no-cache-dir -r /app/requirements.txt

CMD ["/app/run.sh"]
