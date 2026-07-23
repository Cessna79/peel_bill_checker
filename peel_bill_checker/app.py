import json
import os
import time
import bashio

print("=" * 50)
print("Peel Water Bill Checker")
print("Version 1.0.0")
print("=" * 50)


email = bashio.config.get("email")
password = bashio.config.get("password")

print("Configured email:")
print(email)

if password:
    print("Password received")
else:
    print("No password configured")


print("Addon started successfully")


while True:
    print("Checking water bill...")

    # Future:
    # login to Region of Peel
    # check balance
    # create sensor

    time.sleep(3600)
