
import requests
import json

def test_model(model_name):
    print(f"--- Testing {model_name} ---")
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "Say OK"}],
        "max_tokens": 5
    }
    try:
        resp = requests.post("http://127.0.0.1:1234/v1/chat/completions", json=payload, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code != 200:
             print(f"Error Body: {resp.text}")
        else:
             print("Success")
    except Exception as e:
        print(f"Exception: {e}")

models = ["openai/gpt-oss-20b", "jinx-gpt-oss-20b", "mistralai/ministral-3-3b"]

for m in models:
    test_model(m)
