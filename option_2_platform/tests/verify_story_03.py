
import requests
import sys

BASE_URL = "http://localhost:8000"

def test_greeting():
    print("-- Creating Chat checking Greeting --")
    res = requests.post(f"{BASE_URL}/api/chats/global/create")
    if res.status_code != 201:
        print(f"Create failed: {res.status_code}")
        sys.exit(1)
        
    chat_id = res.json()["chat_id"]
    print(f"Chat ID: {chat_id}")
    
    # Get history
    res = requests.get(f"{BASE_URL}/api/chats/global/{chat_id}")
    chat = res.json()
    messages = chat.get("messages", [])
    
    # Expect: System Prompt (hidden/role=system) + Assistant Greeting
    if len(messages) < 2:
        print(f"❌ FAILURE: Expected at least 2 messages (System + Greeting), got {len(messages)}")
        sys.exit(1)
        
    greeting = messages[1]
    print(f"Greeting Message: {greeting['content']}")
    
    expected_partial = "Willkommen beim IFB PROFI-Assistenzsystem"
    if expected_partial not in greeting['content']:
        print(f"❌ FAILURE: Greeting logic ignored config. Expected '{expected_partial}'")
        sys.exit(1)
    
    print("✅ SUCCESS: Greeting matches config.")

if __name__ == "__main__":
    try:
        test_greeting()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
