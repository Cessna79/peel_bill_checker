print("VERSION TEST 1.0.13")

import os
import re
import json
import requests

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)


PEEL_LOGIN = "https://peelregion.idoxs.ca/home"

PEEL_BILLS = "https://peelregion.idoxs.ca/billing/Bills.aspx"

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


        print("Saved bill")


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



            html = page.content()


            with open(
                "/data/peel_debug.html",
                "w",
                encoding="utf-8"
            ) as f:

                f.write(html)



            print("Saved HTML dump")



            body_text = page.locator(
                "body"
            ).inner_text()



            print(
                body_text[:3000]
            )



            print("Searching bill history")



           bill_match = re.search(
               r"You had a bill for\s+\$([\d,]+\.\d+)\s+due on\s+([A-Za-z]+\s+\d+,\s+\d{4})",
               body_text,
               re.MULTILINE
            )

            )



            if not bill_match:

               print("No bill history found")

               print("Searching manually...")

              lines = body_text.splitlines()

              for line in lines:
                  if "You had a bill for" in line:
                       print("FOUND LINE:", repr(line))

              return


            amount = bill_match.group(1)

            due_date = bill_match.group(2)



            data = {


                "amount": "$" + amount,


                "due": due_date,


                "date": ""

            }



            print(
                "Latest bill:"
            )

            print(data)




            old = load_bill()



            if old != data:


                print(
                    "New bill detected"
                )



                save_bill(data)



                notify(

                    f"New Region of Peel water bill\n\n"

                    f"Amount: {data['amount']}\n"

                    f"Due: {data['due']}"

                )



            else:


                print(
                    "No new bill"
                )



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
