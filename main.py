import requests
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

response = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    json={
        "chat_id": CHAT_ID,
        "text": "✅ GitHub Actions 테스트 성공"
    }
)

print(response.text)
