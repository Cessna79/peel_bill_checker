import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os
from datetime import datetime
import paho.mqtt.publish as mqtt_publish


print("=" * 50)
print("Peel Water Bill Checker")
print("Version 1.0.16")
print("=" * 50)


OPTIONS = "/data/options.json"
OUTPUT = "/data/peel_bill.json"


with open(OPTIONS) as f:
    options = json.load(f)


username = options.get("email")
password = options.get("password")

mqtt_host = "core-mosquitto"
mqtt_port = 1883


print("Username loaded:", "YES" if username else "NO")
print("Password loaded:", "YES" if password else "NO")


def publish_mqtt(data):

    try:

        discovery = {

            "name": "Peel Water Bill",

            "unique_id": "peel_water_bill",

            "state_topic":
                "homeassistant/sensor/peel_water_bill/state",

            "json_attributes_topic":
                "homeassistant/sensor/peel_water_bill/attributes",

            "unit_of_measurement": "$",

            "device_class": "monetary",

            "icon": "mdi:water",

            "device": {

                "identifiers": [
                    "peel_bill_checker"
                ],

                "name":
                    "Peel Water Bill Checker",

                "manufacturer":
                    "Cessna79",

                "model":
                    "Home Assistant Addon"

            }

        }


        mqtt_publish.single(

            "homeassistant/sensor/peel_water_bill/config",

            payload=json.dumps(discovery),

            hostname=mqtt_host,

            port=mqtt_port,

            retain=True

        )


        mqtt_publish.single(

            "homeassistant/sensor/peel_water_bill/state",

            payload=str(data["amount_due"]),

            hostname=mqtt_host,

            port=mqtt_port,

            retain=True

        )


        mqtt_publish.single(

            "homeassistant/sensor/peel_water_bill/attributes",

            payload=json.dumps(data),

            hostname=mqtt_host,

            port=mqtt_port,

            retain=True

        )


        print("MQTT published")


    except Exception as e:

        print(
            "MQTT error:",
            e
        )


def check_bill():

    session = requests.Session()


    headers = {

        "User-Agent":
            "Mozilla/5.0 Chrome/150 Safari/537.36",

        "Accept":
            "application/json",

        "Referer":
            "https://peelregion.idoxs.ca/authentication/login",

        "Origin":
            "https://peelregion.idoxs.ca"

    }


    login_url = (
        "https://peelregion.idoxs.ca/"
        "authentication/login"
    )


    print()
    print("Checking Peel bill...")


    login_page = session.get(

        login_url,

        headers=headers

    )


    soup = BeautifulSoup(

        login_page.text,

        "html.parser"

    )


    token = soup.find(

        "input",

        {"name": "__RequestVerificationToken"}

    )


    ncform = soup.find(

        "input",

        {"name": "__ncforminfo"}

    )


    if not token or not ncform:

        raise Exception(
            "Login tokens missing"
        )


    payload = {

        "username":
            (None, username),

        "password":
            (None, password),

        "__RequestVerificationToken":
            (None, token["value"]),

        "__ncforminfo":
            (None, ncform["value"]),

        "g-recaptcha-response":
            (None, "")

    }


    response = session.post(

        login_url,

        files=payload,

        headers=headers

    )


    result = response.json()


    if "redirectToUrl" not in result:

        raise Exception(
            "Login failed"
        )


    print("LOGIN SUCCESS")


    billing_url = (

        "https://peelregion.idoxs.ca"

        + result["redirectToUrl"]

    )


    billing = session.get(

        billing_url,

        headers=headers

    )


    print(
        "Billing status:",
        billing.status_code
    )


    soup = BeautifulSoup(

        billing.text,

        "html.parser"

    )


    text = soup.get_text(

        " ",

        strip=True

    )


    amount = None
    due_date = None


    amount_match = re.search(

        r"Amount Due\*?\s*\$([\d,]+\.\d{2})",

        text

    )


    if amount_match:

        amount = float(

            amount_match.group(1)

            .replace(",", "")

        )


    position = text.find(
        "Amount Due"
    )


    section = text[position:position + 1000]


    date_match = re.search(

        r"([A-Za-z]+\s+\d{1,2},\s+\d{4})",

        section

    )


    if date_match:

        due_date = date_match.group(1)


    old_amount = None


    if os.path.exists(OUTPUT):

        with open(OUTPUT) as f:

            old = json.load(f)

            old_amount = old.get(
                "amount_due"
            )


    data = {

        "amount_due":
            amount,

        "due_date":
            due_date,

        "status":
            "Outstanding"
            if amount and amount > 0
            else "Paid",

        "changed":
            old_amount != amount,

        "last_checked":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "source":
            "Region of Peel"

    }


    with open(OUTPUT, "w") as f:

        json.dump(

            data,

            f,

            indent=4

        )


    print(
        json.dumps(
            data,
            indent=4
        )
    )


    publish_mqtt(data)



while True:

    try:

        check_bill()


    except Exception as e:

        print(
            "ERROR:",
            e
        )


    print(
        "Next check in 24 hours"
    )


    time.sleep(86400)
