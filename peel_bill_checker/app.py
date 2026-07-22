import os
import re
import json
import subprocess
import requests
from playwright.sync_api import sync_playwright


PEEL_LOGIN = "https://peelregion.idoxs.ca/home"
PEEL_BILLS = "https://peelregion.idoxs.ca/billing/bills.aspx"

HA_URL = "http://supervisor/core/api"
HA_TOKEN = os.environ.get("SUPERVISOR_TOKEN")

LAST_FILE = "/data/last_bill.json"


def get_app_config():
    try:
        result = subprocess.check_output(
            ["bashio", "addon", "options"]
        )

        return json.loads(result)

    except Exception as e:
        print("Could not read app configuration:", e)
        return {}


CONFIG = get_app_config()

PEEL_EMAIL = CONFIG.get("peel_email")
PEEL_PASSWORD = CONFIG.get("peel_password")


def ha_update_sensor(bill):
    if not HA_TOKEN:
        print("No Home Assistant token available")
        return

    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "state": bill["bill_date"],
        "attributes": {
            "amount": bill["amount"],
            "due_date": bill["due_date"],
            "bill_date": bill["bill_date"],
            "source": "Region of Peel",
        },
    }

    requests.post(
        f"{HA_URL}/states/sensor.peel_water_bill",
        headers=headers,
        json=payload,
        timeout=10,
    )


def notify(message):
    if not HA_TOKEN:
        print("No Home Assistant token available")
        return

    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }

    data = {
        "title": "💧 Peel Water Bill",
        "message": message,
    }

    requests.post(
        f"{HA_URL}/services/notify/mobile_app_atg",
        headers=headers,
        json=data,
        timeout=10,
    )


def load_last():
    try:
        with open(LAST_FILE, "r") as f:
            return json.load(f)

    except:
        return None


def save_last(data):
    os.makedirs("/data", exist_ok=True)

    with open(LAST_FILE, "w") as f:
        json.dump(data, f)


def check_peel():

    if not PEEL_EMAIL or not PEEL_PASSWORD:
        print("Missing Peel credentials")
        return


    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        print("Opening Peel")

        page.goto(
            PEEL_LOGIN,
            wait_until="networkidle"
        )


        page.fill(
            "#bannerSignInUsername",
            PEEL_EMAIL
        )

        page.fill(
            "#bannerSignInPassword",
            PEEL_PASSWORD
        )


        page.click("#btnSignIn")

        page.wait_for_timeout(5000)


        page.goto(
            PEEL_BILLS,
            wait_until="networkidle"
        )

        page.wait_for_timeout(3000)


        bills = page.locator(
            "#main_BillContainer .table-grid-item"
        )


        count = bills.count()


        if count == 0:
            print("No bills found")
            browser.close()
            return


        text = bills.first.inner_text()

        print(text)


        amount = re.search(
            r"Amount Due\s+\$([\d,]+\.\d+)",
            text
        )

        due = re.search(
            r"Due Date\s+([A-Za-z]+\s+\d+,\s+\d{4})",
            text
        )

        bill_date = re.search(
            r"Bill Date\s+([A-Za-z]+\s+\d+,\s+\d{4})",
            text
        )


        if not amount:
            print("Amount not found")
            browser.close()
            return


        bill = {
            "amount": "$" + amount.group(1),
            "due_date": due.group(1) if due else "",
            "bill_date": bill_date.group(1) if bill_date else "",
        }


        print("Latest bill:", bill)


        old = load_last()


        if old != bill:

            save_last(bill)

            ha_update_sensor(bill)

            notify(
                f"New Region of Peel water bill\n\n"
                f"Amount: {bill['amount']}\n"
                f"Bill date: {bill['bill_date']}\n"
                f"Due: {bill['due_date']}"
            )

        else:
            print("No new bill")


        browser.close()



if __name__ == "__main__":
    check_peel()
