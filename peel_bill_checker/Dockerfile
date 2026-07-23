ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest

FROM ${BUILD_FROM}

WORKDIR /app

RUN apk add --no-cache \
    python3 \
    py3-pip \
    chromium \
    chromium-chromedriver

COPY requirements.txt /app/

RUN pip3 install --no-cache-dir --break-system-packages -r /app/requirements.txt

COPY app.py /app/app.py

CMD ["python3","/app/app.py"]
