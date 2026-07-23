import requests
from bs4 import BeautifulSoup
import time


print("=" * 50)
print("Peel Form Inspector")
print("=" * 50)


session = requests.Session()

url = "https://peelregion.idoxs.ca/authentication/login"

headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}


r = session.get(url, headers=headers)


print("Status:", r.status_code)


soup = BeautifulSoup(r.text, "lxml")


form = soup.find("form")


print("\nFORM DETAILS")

print("Action:")
print(form.get("action"))

print("Method:")
print(form.get("method"))


print("\nHTML ATTRIBUTES:")

for key, value in form.attrs.items():
    print(key, "=", value)


print("\nELEMENTS:")

for e in form.find_all(["input", "button"]):

    print("----------------")
    print("TAG:", e.name)

    for k,v in e.attrs.items():
        print(k, "=", v)


print("\nPossible scripts:")

for script in soup.find_all("script"):

    src = script.get("src")

    if src:
        print(src)


while True:
    time.sleep(3600)
