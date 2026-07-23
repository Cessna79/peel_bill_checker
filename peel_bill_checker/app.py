import requests
from bs4 import BeautifulSoup
import json
import time

print("=" * 50)
print("Peel Water Bill Checker")
print("Login Test")
print("=" * 50)


with open("/data/options.json") as f:
    options = json.load(f)


username = options.get("email")
password = options.get("password")


session = requests.Session()

login_url = "https://peelregion.idoxs.ca/authentication/login"


try:

    print("Getting login page...")

    response = session.get(login_url)

    soup = BeautifulSoup(response.text, "lxml")


    token = soup.find(
        "input",
        {"name": "__RequestVerificationToken"}
    )["value"]


    ncform = soup.find(
        "input",
        {"name": "__ncforminfo"}
    )["value"]


    print("Tokens received")


    login_data = {

        "username": username,
        "password": password,

        "__RequestVerificationToken": token,

        "__ncforminfo": ncform
    }


    print("Sending login...")


    result = session.post(
        login_url,
        data=login_data,
        allow_redirects=True
    )


    print("Login status:", result.status_code)

    print("Final URL:")
    print(result.url)


    if "logout" in result.text.lower():

        print("LOGIN SUCCESS")

    else:

        print("LOGIN RESULT UNKNOWN")


        # Look for error messages
        soup = BeautifulSoup(result.text, "lxml")

        for msg in soup.find_all(
            ["div", "span", "p"]
        ):
            text = msg.get_text(strip=True)

            if "invalid" in text.lower():
                print("Message:", text)



except Exception as e:

    print("ERROR")
    print(e)



while True:
    time.sleep(3600)
