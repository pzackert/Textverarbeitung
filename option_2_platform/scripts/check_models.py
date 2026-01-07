
import requests
import json

try:
    resp = requests.get("http://127.0.0.1:1234/v1/models", timeout=5)
    print(f"Status: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
