ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest

FROM ${BUILD_FROM}

WORKDIR /app

RUN apk add --no-cache python3 py3-pip

COPY app.py /app/app.py
COPY requirements.txt /app/requirements.txt

RUN pip3 install --no-cache-dir -r /app/requirements.txt

CMD ["python3", "/app/app.py"]
