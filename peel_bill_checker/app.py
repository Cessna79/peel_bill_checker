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
print("Version 1.0.26")
print("=" * 50)


OPTIONS = "/data/options.json"
OUTPUT = "/data/peel_bill.json"


with open(OPTIONS) as f:
    options = json.load(f)


username = options.get("email")
password = options.get("password")

mqtt_host = options.get(
    "mqtt_host",
    "core-mosquitto"
)

mqtt_port = int(
    options.get(
        "mqtt_port",
        1883
    )
)

mqtt_username = options.get(
    "mqtt_username"
)

mqtt_password = options.get(
    "mqtt_password"
)


print(
    "Username loaded:",
    "YES" if username else "NO"
)

print(
    "Password loaded:",
    "YES" if password else "NO"
)

print(
    "MQTT Host:",
    mqtt_host
)

print(
    "MQTT Port:",
    mqtt_port
)

print(
    "MQTT Username loaded:",
    "YES" if mqtt_username else "NO"
)

print(
    "MQTT Password loaded:",
    "YES" if mqtt_password else "NO"
)


STATE_TOPIC = (
    "homeassistant/sensor/peel_water_bill/state"
)

ATTR_TOPIC = (
    "homeassistant/sensor/peel_water_bill/attributes"
)

CONFIG_TOPIC = (
    "homeassistant/sensor/peel_water_bill/config"
)


CHANGE_STATE_TOPIC = (
    "homeassistant/binary_sensor/"
    "peel_water_bill_changed/state"
)

CHANGE_CONFIG_TOPIC = (
    "homeassistant/binary_sensor/"
    "peel_water_bill_changed/config"
)


def mqtt_options():

    data = {}

    if mqtt_username:
        data["auth"] = {
            "username": mqtt_username,
            "password": mqtt_password
        }

    return data



def publish_mqtt(data):

    try:

        print("Publishing MQTT...")


        discovery = {

            "name":
                "Peel Water Bill",

            "unique_id":
                "peel_water_bill",

            "state_topic":
                STATE_TOPIC,

            "json_attributes_topic":
                ATTR_TOPIC,

            "unit_of_measurement":
                "$",

            "device_class":
                "monetary",

            "icon":
                "mdi:water",

            "device": {

                "identifiers":
                    [
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


        change_discovery = {

            "name":
                "Peel Water Bill New Bill",

            "unique_id":
                "peel_water_bill_new_bill",

            "state_topic":
                CHANGE_STATE_TOPIC,

            "payload_on":
                "ON",

            "payload_off":
                "OFF",

            "device_class":
                "update",

            "icon":
                "mdi:file-document-alert",

            "device": {

                "identifiers":
                    [
                        "peel_bill_checker"
                    ],

                "name":
                    "Peel Water Bill Checker"

            }

        }


        mqtt_publish.single(
            CONFIG_TOPIC,
            payload=json.dumps(discovery),
            hostname=mqtt_host,
            port=mqtt_port,
            retain=True,
            **mqtt_options()
        )


        mqtt_publish.single(
            CHANGE_CONFIG_TOPIC,
            payload=json.dumps(change_discovery),
            hostname=mqtt_host,
            port=mqtt_port,
            retain=True,
            **mqtt_options()
        )


        mqtt_publish.single(
            STATE_TOPIC,
            payload=str(data["amount_due"]),
            hostname=mqtt_host,
            port=mqtt_port,
            retain=True,
            **mqtt_options()
        )


        mqtt_publish.single(
            ATTR_TOPIC,
            payload=json.dumps(data),
            hostname=mqtt_host,
            port=mqtt_port,
            retain=True,
            **mqtt_options()
        )


        mqtt_publish.single(
            CHANGE_STATE_TOPIC,
            payload="ON" if data["changed"] else "OFF",
            hostname=mqtt_host,
            port=mqtt_port,
            retain=True,
            **mqtt_options()
        )


        print(
            "MQTT published successfully"
        )


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
        headers=headers,
        timeout=30
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
        headers=headers,
        timeout=30
    )


    print(
        "Login response:",
        response.text[:100]
    )


    result = response.json()


    if "redirectToUrl" not in result:

        raise Exception(
            "Login failed"
        )


    print(
        "LOGIN SUCCESS"
    )


    billing_url = (
        "https://peelregion.idoxs.ca"
        + result["redirectToUrl"]
    )


    billing = session.get(
        billing_url,
        headers=headers,
        timeout=30
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


    if position >= 0:

        section = text[
            position:
            position + 1000
        ]


        date_match = re.search(
            r"([A-Za-z]+\s+\d{1,2},\s+\d{4})",
            section
        )


        if date_match:

            due_date = date_match.group(1)



    old_amount = None


    if os.path.exists(OUTPUT):

        try:

            with open(OUTPUT) as f:

                old = json.load(f)

                old_amount = old.get(
                    "amount_due"
                )

        except:

            pass



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


    with open(
        OUTPUT,
        "w"
    ) as f:

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

print(
    "Waiting 30 seconds for Home Assistant services..."
)

time.sleep(30)



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
