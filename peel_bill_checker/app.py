import requests
from bs4 import BeautifulSoup
import json
import time


print("=" * 50)
print("Peel Water Bill Checker")
print("Login Test 1.1.10")
print("=" * 50)


with open("/data/options.json") as f:
    options = json.load(f)


username = options.get("email")
password = options.get("password")


session = requests.Session()


headers = {
    "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 "
        "Chrome/150.0 Safari/537.36",

    "Accept":
        "application/json",

    "Referer":
        "https://peelregion.idoxs.ca/authentication/login",

    "Origin":
        "https://peelregion.idoxs.ca"
}


login_url = "https://peelregion.idoxs.ca/authentication/login"


try:

    print("Loading login page")


    page = session.get(
        login_url,
        headers=headers
    )


    soup = BeautifulSoup(
        page.text,
        "lxml"
    )


    token = soup.find(
        "input",
        {"name": "__RequestVerificationToken"}
    )["value"]


    ncform = soup.find(
        "input",
        {"name": "__ncforminfo"}
    )["value"]


    # IMPORTANT:
    # multipart fields like browser
    payload = {

        "username":
        (None, username),

        "password":
        (None, password),

        "__RequestVerificationToken":
        (None, token),

        "__ncforminfo":
        (None, ncform),

        "g-recaptcha-response":
        (None, "")
    }


    print("Submitting AJAX login")


    response = session.post(
        login_url,
        files=payload,
        headers=headers
    )


    print("Status:")
    print(response.status_code)


    print("Response:")
    print(response.text[:500])


    if response.headers.get(
        "content-type",
        ""
    ).startswith("application/json"):


        result = response.json()


        if "redirectToUrl" in result:

            print("LOGIN SUCCESS")

            billing_url = (
                "https://peelregion.idoxs.ca"
                + result["redirectToUrl"]
            )

            print(
                "Opening:",
                billing_url
            )


            bill = session.get(
                billing_url,
                headers=headers
            )


            print(
                "Billing status:",
                bill.status_code
            )


            print(
                "Billing page length:",
                len(bill.text)
            )


        else:
            print("No redirect received")


    else:

        print("Server did not return JSON")


except Exception as e:

    print("ERROR:")
    print(e)



while True:
    time.sleep(3600)
