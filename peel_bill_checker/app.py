import paho.mqtt.publish as mqtt_publish
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime
import os


print("=" * 50)
print("Peel Water Bill Checker")
print("Version 1.0.14")
print("=" * 50)


OPTIONS = "/data/options.json"
OUTPUT = "/data/peel_bill.json"


with open(OPTIONS) as f:
    options = json.load(f)


username = options.get("email")
password = options.get("password")


print("Username loaded:", "YES" if username else "NO")
print("Password loaded:", "YES" if password else "NO")


def check_bill():

    session = requests.Session()


    headers = {

        "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Chrome/150 Safari/537.36",

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


    billing_url = (
        "https://peelregion.idoxs.ca"
        + result["redirectToUrl"]
    )


    billing = session.get(
        billing_url,
        headers=headers
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


    # Find date near current bill

    pos = text.find(
        "Amount Due"
    )


    section = text[
        pos:
        pos + 1000
    ]


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


    if old_amount != amount:

        print(
            "NEW BILL OR CHANGE DETECTED"
        )

    else:

        print(
            "No change"
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


    with open(
        OUTPUT,
        "w"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )


    print()
    print(
        json.dumps(
            data,
            indent=4
        )
    )


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


    time.sleep(
        86400
    )
