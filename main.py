import os
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URL = "https://www.gojobs.go.kr/apmList.do?menuNo=401&mngrMenuYn=N&selMenuNo=400&upperMenuNo="

KEYWORDS = [
    "청년인턴",
    "청년 인턴"
]


# -------------------------
# Telegram
# -------------------------
def send_telegram(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )


# -------------------------
# Seen load/save
# -------------------------
def load_seen():
    if not os.path.exists("seen_posts.txt"):
        return set()

    with open("seen_posts.txt", "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def save_seen(seen):
    with open("seen_posts.txt", "w", encoding="utf-8") as f:
        for item in sorted(seen):
            f.write(item + "\n")


# -------------------------
# Requests session (retry 적용)
# -------------------------
retry = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET"]
)

session = requests.Session()
adapter = HTTPAdapter(max_retries=retry)

session.mount("http://", adapter)
session.mount("https://", adapter)


# -------------------------
# Load seen posts
# -------------------------
seen = load_seen()


# -------------------------
# Fetch HTML (핵심 안정화 부분)
# -------------------------
try:
    response = session.get(
        URL,
        timeout=(10, 30),
        headers={"User-Agent": "Mozilla/5.0"}
    )
    response.raise_for_status()
    html = response.text

except requests.exceptions.RequestException as e:
    send_telegram(f"🚨 나라일터 접속 실패\n{e}")
    raise


# -------------------------
# Parse
# -------------------------
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


# -------------------------
# Save only if updated
# -------------------------
if updated:
    save_seen(seen)
