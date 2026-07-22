import os
import re
import json
import requests
from playwright.sync_api import sync_playwright


PEEL_LOGIN = "https://peelregion.idoxs.ca/home"
PEEL_BILLS = "https://peelregion.idoxs.ca/billing/bills.aspx"

HA_URL = "http://supervisor/core/api"
HA_TOKEN = os.environ.get("SUPERVISOR_TOKEN")

LAST_FILE = "/data/last_bill.json"


OPTIONS_FILE = "/data/options.json"


def get_app_config():

    try:
        with open(OPTIONS_FILE, "r") as f:
            return json.load(f)

    except Exception as e:
        print("Could not read options:", e)
        return {}


CONFIG = get_app_config()

PEEL_EMAIL = CONFIG.get("peel_email")
PEEL_PASSWORD = CONFIG.get("peel_password")


def notify(message):

    if not HA_TOKEN:
        print("No HA token")
        return

    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }

    requests.post(
        f"{HA_URL}/services/notify/mobile_app_atg",
        headers=headers,
        json={
            "title": "💧 Peel Water Bill",
            "message": message
        },
    )


def save_bill(data):

    with open(LAST_FILE, "w") as f:
        json.dump(data, f)


def load_bill():

    try:
        with open(LAST_FILE) as f:
            return json.load(f)

    except:
        return None


def check_bill():

    if not PEEL_EMAIL or not PEEL_PASSWORD:
        print("Missing Peel credentials")
        return


    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

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


        bill = page.locator(
            "#main_BillContainer .table-grid-item"
        ).first


        text = bill.inner_text()

        print(text)


        amount = re.search(
            r"Amount Due\s+\$([\d,]+\.\d+)",
            text
        )

        due = re.search(
            r"Due Date\s+(.+)",
            text
        )

        date = re.search(
            r"Bill Date\s+(.+)",
            text
        )


        if not amount:
            print("No bill found")
            return


        data = {
            "amount": "$" + amount.group(1),
            "due": due.group(1) if due else "",
            "date": date.group(1) if date else "",
        }


        print(data)


        old = load_bill()


        if old != data:

            save_bill(data)

            notify(
                f"New Region of Peel bill\n\n"
                f"Amount: {data['amount']}\n"
                f"Bill date: {data['date']}\n"
                f"Due: {data['due']}"
            )

        else:

            print("No new bill")


        browser.close()



if __name__ == "__main__":
    check_bill()
