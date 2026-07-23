import requests
from bs4 import BeautifulSoup
import json
import time


print("=" * 50)
print("Peel Water Bill Checker")
print("Login Debug Version 1.0.5")
print("=" * 50)


OPTIONS = "/data/options.json"

with open(OPTIONS) as f:
    options = json.load(f)


username = options.get("email")
password = options.get("password")


print("Username loaded:", username)

if password:
    print("Password loaded: YES")
else:
    print("Password loaded: NO")


session = requests.Session()

# Act like a normal browser
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,"
              "application/xml;q=0.9,*/*;q=0.8"
}


login_url = "https://peelregion.idoxs.ca/authentication/login"


try:

    print("\nOpening login page...")

    page = session.get(
        login_url,
        headers=headers
    )


    print("Login page status:", page.status_code)


    soup = BeautifulSoup(
        page.text,
        "lxml"
    )


    print("\nGetting form fields:")


    form = soup.find("form")


    login_data = {}


    if form:

        for inp in form.find_all("input"):

            name = inp.get("name")
            value = inp.get("value", "")

            if name:
                print(
                    name,
                    "=",
                    value[:50]
                )

                login_data[name] = value


    # Add credentials
    login_data["username"] = username
    login_data["password"] = password


    print("\nSubmitting login...")


    result = session.post(
        login_url,
        data=login_data,
        headers=headers,
        allow_redirects=True
    )


    print("\nLogin response status:")
    print(result.status_code)


    print("\nFinal URL:")
    print(result.url)


    print("\nCookies after login:")

    for cookie in session.cookies:
        print(
            cookie.name,
            "=",
            cookie.value[:30],
            "..."
        )


    soup = BeautifulSoup(
        result.text,
        "lxml"
    )


    print("\nPage title:")

    title = soup.find("title")

    if title:
        print(title.text.strip())


    print("\nSearching for messages:")


    found = False

    for text in soup.stripped_strings:

        words = [
            "invalid",
            "incorrect",
            "error",
            "failed",
            "wrong",
            "password",
            "username"
        ]

        if any(
            word in text.lower()
            for word in words
        ):

            print("-", text)
            found = True


    if not found:
        print("No error message found")


    print("\nChecking login status:")


    if "logout" in result.text.lower():

        print("LOGIN SUCCESS")

    elif "dashboard" in result.text.lower():

        print("LOGIN POSSIBLY SUCCESSFUL")

    else:

        print("LOGIN NOT CONFIRMED")


    print("\nForms remaining on page:")

    for f in soup.find_all("form"):

        print("----------------")
        print(
            "Action:",
            f.get("action")
        )

        for inp in f.find_all("input"):

            print(
                inp.get("name"),
                inp.get("type")
            )


except Exception as e:

    print("\nERROR OCCURRED:")
    print(e)



print("\nAddon running...")


while True:
    time.sleep(3600)
