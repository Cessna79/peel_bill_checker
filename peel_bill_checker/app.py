import requests
from bs4 import BeautifulSoup
import json
import time
import re


print("=" * 50)
print("Peel Water Bill Checker")
print("Version 1.0.12")
print("=" * 50)


OPTIONS = "/data/options.json"


# Load Home Assistant addon options
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
            "Login tokens missing"
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


    print("Tokens received")

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
            "Login unsuccessful"
        )


    print()
    print("LOGIN SUCCESS")


    billing_url = (
        "https://peelregion.idoxs.ca"
        + result["redirectToUrl"]
    )


    print()
    print("Opening billing page:")
    print(billing_url)


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


    # Save HTML for backup/debug

    with open(
        "/tmp/billing.html",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            billing.text
        )


    print("Billing HTML saved")


    print()
    print("=" * 50)
    print("Searching billing page")
    print("=" * 50)


    text = billing.text


    keywords = [
        "amount",
        "balance",
        "due",
        "bill",
        "payment",
        "account"
    ]


    lower_text = text.lower()


    for word in keywords:

        if word in lower_text:

            print(
                "Found keyword:",
                word
            )


    print()
    print("=" * 50)
    print("Dollar amount details")
    print("=" * 50)


    amounts_found = set()


    for match in re.finditer(
        r"\$[\d,]+\.\d{2}",
        text
    ):


        amount = match.group()


        if amount in amounts_found:
            continue


        amounts_found.add(amount)


        start = max(
            0,
            match.start() - 200
        )

        end = min(
            len(text),
            match.end() + 200
        )


        nearby = text[start:end]


        # Clean HTML
        nearby = BeautifulSoup(
            nearby,
            "html.parser"
        ).get_text(
            " ",
            strip=True
        )


        print()
        print("AMOUNT FOUND:")
        print(amount)

        print("CONTEXT:")
        print(nearby)

        print("-" * 60)



    print()
    print("Extraction complete")


except Exception as e:

    print()
    print("ERROR:")
    print(e)



print()
print("Addon running...")


while True:

    time.sleep(3600)
