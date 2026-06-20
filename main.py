import telegram
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

bot = telegram.Bot(token=BOT_TOKEN)

bot.send_message(
    chat_id=CHAT_ID,
    text="✅ GitHub Actions 테스트 성공"
)
