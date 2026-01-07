
import requests

BASE_URL = "http://localhost:8000"

resp = requests.get(f"{BASE_URL}/projects")
print(resp.text)
