import json
import os
import time

print("=" * 50)
print("Peel Water Bill Checker")
print("Version 1.0.2")
print("=" * 50)

OPTIONS = "/data/options.json"

if os.path.exists(OPTIONS):

    with open(OPTIONS) as f:
        options = json.load(f)

    email = options.get("email")
    password = options.get("password")

    print("Email:", email)

    if password:
        print("Password received: YES")
    else:
        print("Password received: NO")

else:
    print("No options file found")


print("Addon started successfully")

while True:
    print("Waiting for bill check...")
    time.sleep(3600)
