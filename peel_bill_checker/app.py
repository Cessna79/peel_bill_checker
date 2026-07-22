print("VERSION TEST 1.0.14")

import os
import re
import json
import requests

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)


PEEL_LOGIN = "https://peelregion.idoxs.ca/home"

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

        print("Notification error:", e)




def save_bill(data):

    try:

        with open(LAST_FILE, "w") as f:
            json.dump(data, f)

        print("Bill saved")


    except Exception as e:

        print("Save error:", e)




def load_bill():

    try:

        with open(LAST_FILE, "r") as f:
            return json.load(f)

    except:

        return None




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


            print("Opening Peel login")


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

            print("Email entered")



            page.fill(
                "#bannerSignInPassword",
                PEEL_PASSWORD
            )

            print("Password entered")



            page.click(
                "#btnSignIn"
            )

            print("Clicked login")



            page.wait_for_timeout(7000)



            print(
                "After login URL:",
                page.url
            )



            print("Opening billing home")



            page.goto(
                "https://peelregion.idoxs.ca/billing/home.aspx",
                wait_until="domcontentloaded",
                timeout=60000
            )


            print("Billing home loaded")

            print(
                "Current URL:",
                page.url
            )



            body_text = page.locator(
                "body"
            ).inner_text()



            with open(
                "/data/peel_debug.html",
                "w",
                encoding="utf-8"
            ) as f:

                f.write(page.content())


            print("Saved HTML dump")


            print(body_text[:3000])



            print("Searching bill history")



            lines = body_text.splitlines()



            bill_line = None


            for line in lines:

                if "You had a bill for" in line:

                    bill_line = line.strip()

                    break



            if not bill_line:


                print("No bill history found")

                return



            print(
                "Found bill line:",
                bill_line
            )



            match = re.search(

                r"You had a bill for\s+\$([\d,]+\.\d+)\s+due on\s+(.+)",

                bill_line

            )



            if not match:


                print("Could not parse bill line")

                return



            amount = match.group(1)

            due = match.group(2)



            data = {

                "amount": "$" + amount,

                "due": due,

                "date": ""

            }



            print(
                "Latest bill:"
            )

            print(data)



            old = load_bill()



            if old != data:


                print("New bill detected")


                save_bill(data)



                notify(

                    f"New Region of Peel water bill\n\n"

                    f"Amount: {data['amount']}\n"

                    f"Due: {data['due']}"

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
