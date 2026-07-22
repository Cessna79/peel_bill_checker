ARG BUILD_FROM

FROM $BUILD_FROM

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

RUN pip3 install playwright

RUN playwright install chromium

COPY app.py /app/app.py
COPY run.sh /app/run.sh

RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]
