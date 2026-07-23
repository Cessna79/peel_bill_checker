import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime


print("=" * 50)
print("Peel Water Bill Checker")
print("Version 1.0.13")
print("=" * 50)


OPTIONS = "/data/options.json"
OUTPUT = "/data/peel_bill.json"


# Load addon settings

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
        "AppleWebKit/537.36 Chrome/150 Safari/537.36",

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


    login_page = session.get(
        login_url,
        headers=headers
    )


    soup = BeautifulSoup(
        login_page.text,
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


    print("Submitting login...")


    response = session.post(
        login_url,
        files=payload,
        headers=headers
    )


    print("Login response:")
    print(response.text)


    login_result = response.json()


    if "redirectToUrl" not in login_result:

        raise Exception(
            "Login failed"
        )


    print("LOGIN SUCCESS")


    billing_url = (
        "https://peelregion.idoxs.ca"
        + login_result["redirectToUrl"]
    )


    print("Opening billing page...")


    billing = session.get(
        billing_url,
        headers=headers
    )


    print(
        "Billing status:",
        billing.status_code
    )


    html = billing.text


    # Save page for debugging

    with open(
        "/tmp/billing.html",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html)


    soup = BeautifulSoup(
        html,
        "html.parser"
    )


    clean_text = soup.get_text(
        " ",
        strip=True
    )


    print()
    print("=" * 50)
    print("Extracting bill information")
    print("=" * 50)


    bill_amount = None
    due_date = None


    # Find Amount Due

    amount_match = re.search(
        r"Amount Due\*?\s*\$([\d,]+\.\d{2})",
        clean_text
    )


    if amount_match:

        bill_amount = (
            amount_match.group(1)
            .replace(",", "")
        )

        print(
            "Amount Due:",
            bill_amount
        )


    else:

        print(
            "Amount Due not found"
        )


    # Try to find due date

    date_patterns = [

        r"Due Date\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})",

        r"due on\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})",

        r"Payment Due\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})"

    ]


    for pattern in date_patterns:

        match = re.search(
            pattern,
            clean_text,
            re.IGNORECASE
        )

        if match:

            due_date = match.group(1)

            print(
                "Due Date:",
                due_date
            )

            break


    if not due_date:

        print(
            "Due date not found"
        )


    result = {

        "amount_due":
            bill_amount,

        "due_date":
            due_date,

        "checked":
            datetime.now().isoformat(),

        "status":
            "success"

    }


    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=4
        )


    print()
    print("Saved:")
    print(json.dumps(result, indent=4))


except Exception as e:

    print()
    print("ERROR:")
    print(e)


print()
print("Addon running...")


while True:

    time.sleep(3600)
