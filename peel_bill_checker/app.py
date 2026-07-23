import requests
from bs4 import BeautifulSoup
import json
import time
import re


print("=" * 50)
print("Peel Water Bill Checker")
print("Version 1.0.11")
print("=" * 50)


OPTIONS = "/data/options.json"


with open(OPTIONS) as f:
    options = json.load(f)


username = options.get("email")
password = options.get("password")


print("Username loaded:", "YES" if username else "NO")
print("Password loaded:", "YES" if password else "NO")


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


login_url = (
    "https://peelregion.idoxs.ca/"
    "authentication/login"
)


try:

    print()
    print("Opening login page...")


    page = session.get(
        login_url,
        headers=headers
    )


    print(
        "Login page status:",
        page.status_code
    )


    soup = BeautifulSoup(
        page.text,
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
            "Security tokens not found"
        )


    token = token["value"]
    ncform = ncform["value"]


    print("Tokens received")


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


    print("Submitting login...")


    response = session.post(
        login_url,
        files=payload,
        headers=headers
    )


    print()
    print("Login response:")
    print(response.text)


    result = response.json()


    if "redirectToUrl" not in result:

        raise Exception(
            "Login failed"
        )


    print()
    print("LOGIN SUCCESS")


    billing_url = (
        "https://peelregion.idoxs.ca"
        + result["redirectToUrl"]
    )


    print(
        "Opening billing page:"
    )

    print(
        billing_url
    )


    billing = session.get(
        billing_url,
        headers={
            "User-Agent":
            headers["User-Agent"]
        }
    )


    print()
    print(
        "Billing status:",
        billing.status_code
    )


    print(
        "Billing page size:",
        len(billing.text)
    )


    # Save page for inspection

    with open(
        "/tmp/billing.html",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            billing.text
        )


    print(
        "Billing HTML saved"
    )


    print()
    print(
        "Searching page..."
    )


    text = billing.text.lower()


    keywords = [

        "amount",

        "balance",

        "due",

        "invoice",

        "bill",

        "payment",

        "account"

    ]


    for word in keywords:

        if word in text:

            print(
                "Found:",
                word
            )


    print()
    print(
        "Looking for dollar amounts..."
    )


    amounts = re.findall(
        r"\$[\d,]+\.\d{2}",
        billing.text
    )


    for amount in amounts[:20]:

        print(
            "Amount:",
            amount
        )


    print()
    print(
        "Searching complete"
    )


except Exception as e:

    print()
    print("ERROR:")
    print(e)



print()
print(
    "Addon running..."
)


while True:

    time.sleep(3600)
