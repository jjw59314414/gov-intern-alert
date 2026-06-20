import requests
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

print("START")
print("CHAT_ID =", CHAT_ID)

r = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    json={
        "chat_id": CHAT_ID,
        "text": "테스트"
    }
)

print("STATUS =", r.status_code)
print("BODY =", r.text)

raise Exception("FORCE STOP")
