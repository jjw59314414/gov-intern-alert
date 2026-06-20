import requests
from bs4 import BeautifulSoup
import telegram
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

KEYWORDS = [
    "청년인턴",
    "청년 인턴",
    "인턴",
    "체험형"
]

SITES = [
    "https://www.moleg.go.kr",
    "https://www.moj.go.kr",
    "https://www.opm.go.kr"
]

bot = telegram.Bot(token=BOT_TOKEN)

for site in SITES:
    try:
        r = requests.get(site, timeout=10)

        text = r.text

        for keyword in KEYWORDS:

            if keyword in text:

                bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"공고 발견 가능성\n{site}\n키워드:{keyword}"
                )

                break

    except:
        pass
