ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:latest

FROM ${BUILD_FROM}

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

RUN playwright install chromium

COPY app.py /app/app.py

CMD ["python3", "/app/app.py"]
