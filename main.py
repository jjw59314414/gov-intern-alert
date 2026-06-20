import os
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URL = "https://www.gojobs.go.kr/apmList.do?menuNo=401&mngrMenuYn=N&selMenuNo=400&upperMenuNo="

KEYWORDS = [
    "청년인턴",
    "청년 인턴"
]


def send_telegram(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )


def load_seen():
    if not os.path.exists("seen_posts.txt"):
        return set()

    with open("seen_posts.txt", "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def save_seen(seen):
    with open("seen_posts.txt", "w", encoding="utf-8") as f:
        for item in sorted(seen):
            f.write(item + "\n")


seen = load_seen()

html = requests.get(URL, timeout=60).text
soup = BeautifulSoup(html, "html.parser")

rows = soup.select("tbody tr")

updated = False

for row in rows:
    a = row.find("a")

    if not a:
        continue

    title = a.get_text(" ", strip=True)

    if not any(k in title for k in KEYWORDS):
        continue

    href = a.get("href", "")

    try:
        post_id = href.split("'")[3]
    except:
        continue

    if post_id in seen:
        continue

    tds = row.find_all("td")

    agency = tds[2].get_text(" ", strip=True)
    post_date = tds[3].get_text(" ", strip=True)

    msg = f"""🔔 청년인턴 공고 발견

기관: {agency}

제목:
{title}

게시일:
{post_date}

공고번호:
{post_id}
"""

    send_telegram(msg)

    seen.add(post_id)
    updated = True

if updated:
    save_seen(seen)
