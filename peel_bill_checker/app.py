import requests
from bs4 import BeautifulSoup
import json
import time

print("=" * 50)
print("Peel Water Bill Checker")
print("Login Inspector")
print("=" * 50)


with open("/data/options.json") as f:
    options = json.load(f)


email = options.get("email")
password = options.get("password")


session = requests.Session()

login_url = "https://peelregion.idoxs.ca/authentication/login"


try:

    print("Opening login page...")

    r = session.get(login_url)

    print("Status:", r.status_code)

    print("Cookies:")
    print(session.cookies)


    soup = BeautifulSoup(r.text, "lxml")


    print("\nForms found:")

    for form in soup.find_all("form"):
        print("----------------")
        print("Action:", form.get("action"))

        for inp in form.find_all("input"):
            print(
                inp.get("name"),
                inp.get("type"),
                inp.get("value")
            )


except Exception as e:
    print("ERROR")
    print(e)


while True:
    time.sleep(3600)
