import requests
import json
from collections import Counter
import time

# Replace with your actual external IP and port
URL = "https://chatbackendapp.politeglacier-bf110107.swedencentral.azurecontainerapps.io/chat"

counts = Counter()

for i in range(10):
    try:
        resp = requests.post(URL, json={"message": "hi"}, timeout=10)
        data = resp.json()
        model = data.get("model", "unknown")

        # Group models by main family ignoring date suffix
        if model.startswith("gpt-4.1"):
            counts["gpt-4.1"] += 1
        elif model.startswith("gpt-4o"):
            counts["gpt-4o"] += 1
        else:
            counts["other"] += 1

        print(f"{i+1}. {model}")

    except Exception as e:
        counts["error"] += 1
        print(f"{i+1}. Error: {e}")

    time.sleep(0.1)  # small pause to avoid overwhelming server

print("\n=== Final Counts ===")
for model_name, count in counts.items():
    print(f"{model_name}: {count}")