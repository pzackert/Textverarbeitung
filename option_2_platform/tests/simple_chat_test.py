import requests
try:
    # Create Chat
    r = requests.post("http://localhost:8000/api/chats/global")
    cid = r.json()["id"]
    print(f"Chat ID: {cid}")
    # Send Message
    r2 = requests.post(f"http://localhost:8000/api/chats/global/{cid}/message", json={"message": "Wer bist du?"})
    print(f"Status: {r2.status_code}")
    print(f"Response: {r2.text}")
except Exception as e:
    print(e)
