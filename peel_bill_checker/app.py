print("VERSION TEST 1.0.16")

import os
import re
import json
import time
import requests

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)


PEEL_LOGIN = "https://peelregion.idoxs.ca/home"
PEEL_HOME = "https://peelregion.idoxs.ca/billing/home.aspx"

HA_URL = "http://supervisor/core/api"
HA_TOKEN = os.environ.get("SUPERVISOR_TOKEN")

LAST_FILE = "/data/last_bill.json"
OPTIONS_FILE = "/data/options.json"


def get_config():

    try:
        with open(OPTIONS_FILE, "r") as f:
            return json.load(f)

    except Exception as e:
        print("Config error:", e)
        return {}


CONFIG = get_config()

PEEL_EMAIL = CONFIG.get("peel_email")
PEEL_PASSWORD = CONFIG.get("peel_password")


def notify(message):

    if not HA_TOKEN:
        print("No HA token")
        return

    try:

        requests.post(
            f"{HA_URL}/services/notify/mobile_app_atg",
            headers={
                "Authorization": f"Bearer {HA_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "title": "💧 Peel Water Bill",
                "message": message
            },
            timeout=10
        )

        print("Notification sent")

    except Exception as e:
        print("Notify error:", e)



def save_bill(data):

    with open(LAST_FILE, "w") as f:
        json.dump(data, f)



def load_bill():

    try:
        with open(LAST_FILE, "r") as f:
            return json.load(f)

    except:

        return None



def login(page):

    for attempt in range(1,4):

        print(f"Login attempt {attempt}/3")

        try:

            page.goto(
                PEEL_LOGIN,
                wait_until="domcontentloaded",
                timeout=60000
            )

            print("Login page loaded")


            page.wait_for_selector(
                "#bannerSignInUsername",
                timeout=30000
            )


            print("Login form found")


            page.fill(
                "#bannerSignInUsername",
                PEEL_EMAIL
            )


            page.fill(
                "#bannerSignInPassword",
                PEEL_PASSWORD
            )


            print("Credentials entered")


            page.click("#btnSignIn")


            page.wait_for_timeout(5000)


            print(
                "After login:",
                page.url
            )


            if "billing" in page.url:

                return True


        except Exception as e:

            print(
                f"Login attempt {attempt} failed:",
                e
            )

            time.sleep(5)


    return False



def extract_bill(text):

    print("Searching account activity")


    # Example:
    # You had a bill for $1,112.93 due on June 24, 2026

    match = re.search(
        r"You had a bill for \$([\d,]+\.\d+)\s+due on\s+([A-Za-z]+\s+\d+,\s+\d{4})",
        text
    )


    if not match:

        print("No bill history found")
        return None


    amount = "$" + match.group(1)

    due = match.group(2)


    data = {

        "amount": amount,

        "due": due,

        "date": ""

    }


    return data



def check_bill():

    print("Starting bill check")


    if not PEEL_EMAIL or not PEEL_PASSWORD:

        print("Missing Peel credentials")
        return



    with sync_playwright() as p:


        browser = p.chromium.launch(
            headless=True
        )


        page = browser.new_page()


        try:


            if not login(page):

                print("Login failed")
                return



            print("Opening billing home")


            page.goto(
                PEEL_HOME,
                wait_until="domcontentloaded",
                timeout=60000
            )


            print("Billing home loaded")


            print(
                "Current URL:",
                page.url
            )


            page.wait_for_timeout(5000)



            text = page.locator(
                "body"
            ).inner_text()


            with open(
                "/data/peel_debug.html",
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    page.content()
                )


            print(text[:2000])



            bill = extract_bill(text)



            if not bill:

                return



            print(
                "Latest bill:",
                bill
            )



            old = load_bill()



            if old != bill:


                print("New bill detected")


                save_bill(
                    bill
                )


                notify(
                    f"New Region of Peel water bill\n\n"
                    f"Amount: {bill['amount']}\n"
                    f"Due: {bill['due']}"
                )


            else:


                print("No new bill")



        except PlaywrightTimeoutError as e:

            print(
                "Playwright timeout:",
                e
            )


        except Exception as e:

            print(
                "Error:",
                e
            )


        finally:

            browser.close()



if __name__ == "__main__":

    check_bill()
