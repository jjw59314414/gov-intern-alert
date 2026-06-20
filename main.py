import requests
import os
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URL = "https://www.gojobs.go.kr/apmList.do?menuNo=401&mngrMenuYn=N&selMenuNo=400&upperMenuNo="

KEYWORDS = [
    "청년인턴",
    "청년 인턴",
    "인턴"
]

def send_telegram(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )

try:
    html = requests.get(URL, timeout=20).text

    found = False

    for keyword in KEYWORDS:
        if keyword in html:
            send_telegram(
                f"🔔 나라일터에서 '{keyword}' 키워드 발견\n{URL}"
            )
            found = True
            break

    if not found:
        print("No keyword found")

except Exception as e:
    send_telegram(f"오류 발생: {e}")
