print("Starting Peel Water Bill Checker VERSION 1.0.31")

import os
import re
import json
import time
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


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

PEEL_EMAIL = CONFIG.get("email")
PEEL_PASSWORD = CONFIG.get("password")



def notify(message):

    if not HA_TOKEN:
        print("No HA token")
        return

    try:

        requests.post(
            f"{HA_URL}/services/notify/mobile_app_atg",

            headers={
                "Authorization": f"Bearer {HA_TOKEN}",
                "Content-Type": "application/json"
            },

            json={
                "title": "💧 Peel Water Bill",
                "message": message
            },

            timeout=10
        )

        print("Notification sent")

    except Exception as e:
        print("Notification error:", e)



def save_bill(data):

    with open(LAST_FILE, "w") as f:
        json.dump(data, f)



def load_bill():

    try:

        with open(LAST_FILE, "r") as f:
            return json.load(f)

    except:

        return None



def create_driver():

    options = Options()

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        options=options
    )

    return driver



def login(driver):

    print("Opening Peel login")

    driver.get(PEEL_LOGIN)

    time.sleep(5)

    print("Login page loaded")


    try:

        email = driver.find_element(
            By.ID,
            "bannerSignInUsername"
        )

        password = driver.find_element(
            By.ID,
            "bannerSignInPassword"
        )

        print("Login form found")


        email.send_keys(
            PEEL_EMAIL
        )

        password.send_keys(
            PEEL_PASSWORD
        )


        button = driver.find_element(
            By.ID,
            "btnSignIn"
        )

        button.click()


        time.sleep(8)


        print(
            "After login:",
            driver.current_url
        )


        if "billing" in driver.current_url:

            return True


    except Exception as e:

        print(
            "Login error:",
            e
        )


    return False



def extract_bill(text):

    print("Searching account activity")


    text = text.replace(
        "\xa0",
        " "
    )

    text = " ".join(
        text.split()
    )


    matches = re.findall(

        r"You had a bill for\s+\$([\d,]+\.\d+)\s+due on\s+([A-Za-z]+\s+\d+,\s+\d{4})",

        text

    )


    if not matches:

        print("No bill history found")

        return None



    amount, due = matches[0]


    bill = {

        "amount": "$" + amount,

        "due": due

    }


    print(
        "Bill extracted:",
        bill
    )


    return bill



def check_bill():

    print("Starting bill check")


    if not PEEL_EMAIL or not PEEL_PASSWORD:

        print("Missing Peel credentials")

        return



    driver = None


    try:

        driver = create_driver()


        if not login(driver):

            print("Login failed")

            return



        print("Opening billing home")


        driver.get(
            PEEL_HOME
        )


        time.sleep(5)


        print(
            "Current URL:",
            driver.current_url
        )


        html = driver.page_source


        with open(
            "/data/peel_debug.html",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(html)



        text = driver.find_element(
            By.TAG_NAME,
            "body"
        ).text



        print(
            text[:3000]
        )



        bill = extract_bill(text)


        if not bill:

            return



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



    except Exception as e:

        print(
            "Error:",
            e
        )


    finally:

        if driver:

            driver.quit()



if __name__ == "__main__":

    check_bill()
