import requests
from bs4 import BeautifulSoup
import json
import time


print("=" * 50)
print("Peel Water Bill Checker")
print("Login Debug Version 1.0.6")
print("=" * 50)


with open("/data/options.json") as f:
    options = json.load(f)


username = options.get("email")
password = options.get("password")


session = requests.Session()


headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120 Safari/537.36"
    ),
    "Referer": "https://peelregion.idoxs.ca/authentication/login",
    "Origin": "https://peelregion.idoxs.ca"
}


login_url = "https://peelregion.idoxs.ca/authentication/login"


try:

    print("Opening login page")

    r = session.get(
        login_url,
        headers=headers
    )


    soup = BeautifulSoup(
        r.text,
        "lxml"
    )


    form = soup.find("form")


    data = {}


    print("\nAll form elements:")


    for element in form.find_all(
        ["input", "button"]
    ):

        name = element.get("name")
        value = element.get("value", "")

        print(
            element.name,
            name,
            value
        )

        if name:
            data[name] = value


    data["username"] = username
    data["password"] = password


    print("\nSending:")

    for k in data:
        if "password" not in k.lower():
            print(k, "=", data[k][:40])


    result = session.post(
        login_url,
        data=data,
        headers=headers,
        allow_redirects=False
    )


    print("\nResponse:")
    print(result.status_code)

    print("Location header:")
    print(
        result.headers.get("Location")
    )


    print("\nCookies:")

    for c in session.cookies:
        print(c.name)


except Exception as e:

    print("ERROR:")
    print(e)



while True:
    time.sleep(3600)
