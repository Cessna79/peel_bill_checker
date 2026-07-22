ARG BUILD_FROM

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install --with-deps chromium

COPY app.py .
COPY run.sh .

RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]
