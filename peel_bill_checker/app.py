import json
import os
import time

print("=" * 50)
print("Peel Water Bill Checker")
print("Version 1.0.0")
print("=" * 50)

OPTIONS = "/data/options.json"

if os.path.exists(OPTIONS):
    with open(OPTIONS) as f:
        options = json.load(f)

    print("Loaded options:")
    print(options)

else:
    print("No options file found.")

print("Addon started successfully.")

while True:
    time.sleep(60)
