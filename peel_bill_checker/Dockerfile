ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest

FROM ${BUILD_FROM}

WORKDIR /app

RUN apk add --no-cache \
    python3 \
    py3-pip \
    chromium \
    chromium-chromedriver

COPY requirements.txt /app/requirements.txt

RUN pip3 install --no-cache-dir --break-system-packages -r /app/requirements.txt

RUN playwright install chromium

COPY app.py /app/app.py

CMD ["python3", "/app/app.py"]
