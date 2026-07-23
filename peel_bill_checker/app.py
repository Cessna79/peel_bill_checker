import requests
from bs4 import BeautifulSoup
import json
import time


print("=" * 50)
print("Peel Water Bill Checker")
print("Login Success Test 1.0.9")
print("=" * 50)


with open("/data/options.json") as f:
    options = json.load(f)


username = options.get("email")
password = options.get("password")


session = requests.Session()


headers = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120 Safari/537.36",

    "Accept": "application/json",

    "Referer":
        "https://peelregion.idoxs.ca/authentication/login",

    "Origin":
        "https://peelregion.idoxs.ca"
}


login_url = "https://peelregion.idoxs.ca/authentication/login"


try:

    print("Opening login page")

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


    login_data = {

        "username": username,

        "password": password,

        "__RequestVerificationToken": token,

        "__ncforminfo": ncform
    }


    print("Sending login")


    response = session.post(
        login_url,
        files=login_data,
        headers=headers
    )


    print("Login response:")

    print(response.text)


    result = response.json()


    if "redirectToUrl" in result:

        next_page = (
            "https://peelregion.idoxs.ca"
            + result["redirectToUrl"]
        )


        print("Login successful")

        print("Opening:")
        print(next_page)


        bill_page = session.get(
            next_page,
            headers={
                "User-Agent":
                headers["User-Agent"]
            }
        )


        print(
            "Billing page status:",
            bill_page.status_code
        )


        print(
            "Billing page size:",
            len(bill_page.text)
        )


        with open(
            "/tmp/billing.html",
            "w"
        ) as f:
            f.write(bill_page.text)


        print(
            "Saved billing page"
        )


    else:

        print("Login failed")


except Exception as e:

    print("ERROR:")
    print(e)


while True:
    time.sleep(3600)
