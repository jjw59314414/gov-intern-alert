import os
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# -------------------------
# ENV
# -------------------------
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URL = "https://www.gojobs.go.kr/apmList.do?menuNo=401&mngrMenuYn=N&selMenuNo=400&upperMenuNo="

KEYWORDS = ["청년인턴", "청년 인턴"]

SEEN_FILE = "seen_posts.txt"


# -------------------------
# Telegram
# -------------------------
def send_telegram(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": msg
            },
            timeout=10
        )
    except Exception as e:
        print("텔레그램 전송 실패:", e)


# -------------------------
# Seen load/save
# -------------------------
def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()

    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        for item in sorted(seen):
            f.write(item + "\n")


# -------------------------
# HTTP Session (Retry)
# -------------------------
def create_session():
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=3,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False
    )

    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry)

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


session = create_session()


# -------------------------
# Main Logic
# -------------------------
def main():
    seen = load_seen()

    # -------------------------
    # Fetch HTML
    # -------------------------
    try:
        response = session.get(
            URL,
            timeout=(30, 120),
            headers={"User-Agent": "Mozilla/5.0"}
        )
        response.raise_for_status()
        html = response.text

    except Exception as e:
        send_telegram(f"나라일터 접속 시도\n{e}")
        print("크롤링 실패:", e)
        return

    # -------------------------
    # Parse HTML
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

        agency = tds[2].get_text(" ", strip=True) if len(tds) > 2 else "기관정보 없음"
        post_date = tds[3].get_text(" ", strip=True) if len(tds) > 3 else "날짜 없음"

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
    # Save only if new data
    # -------------------------
    if updated:
        save_seen(seen)


# -------------------------
# Entry Point (Render Cron)
# -------------------------
if __name__ == "__main__":
    main()
