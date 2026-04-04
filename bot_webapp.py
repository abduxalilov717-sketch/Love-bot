import logging
import random
import httpx
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8782299050:AAGhdm8O1LVXUKdvRzi4Gc4Wp7zjuq-Wl4A"
CHAT_ID = "-5119427484"
SEND_HOUR = 4
SEND_MINUTE = 0
BASE_URL = "https://abduxalilov717-sketch.github.io/Love-bot"
BIN_ID = "69cf7db6856a682189f67635"
API_KEY = "$2a$10$vrr04luN8fRaLFxvBr09EOjRRIBm75kKW1EQJY7SBhElJaa1KZXUu"
BIN_URL = "https://api.jsonbin.io/v3/b/" + BIN_ID
HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

QUOTES = [
    "Lubov - eto to, chto my stroim vmeste.",
    "Nastoyashchaya lubov - kogda schaste drugogo vazhnee svoego.",
    "Ty - moy lyubimyy chelovek v etom mire.",
    "Kazhdyy den ryadom s toboy - eto podarok.",
    "Ty delaesh kazhdyy moy den luchshe.",
]


def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Tsitata o lyubvi", web_app=WebAppInfo(url=BASE_URL + "/webapp.html"))],
        [InlineKeyboardButton("Viktorina pro menya", web_app=WebAppInfo(url=BASE_URL + "/quiz.html"))],
        [InlineKeyboardButton("Nashi foto", web_app=WebAppInfo(url=BASE_URL + "/photos.html"))],
    ])


async def fetch_quote():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get("https://api.quotable.io/random", params={"tags": "love", "maxLength": 150})
            if r.status_code == 200:
                d = r.json()
                return "'" + d.get("content", "") + "' - " + d.get("author", "")
    except Exception:
        pass
    return random.choice(QUOTES)


async def send_daily_quote(bot):
    quote = await fetch_quote()
    now = datetime.now().strftime("%d.%m.%Y")
    await bot.send_message(
        chat_id=CHAT_ID,
        text="Dobroye utro, moya lyubov!\n\n" + quote + "\n\nYa vsegda dumay o tebe\n" + now,
        reply_markup=main_keyboard()
    )
    logger.info("Daily quote sent!")


async def cmd_start(update, context):
    await update.message.reply_text("Privet! Vyberi chto otkryt:", reply_markup=main_keyboard())


async def cmd_sendnow(update, context):
    await send_daily_quote(context.bot)
    await update.message.reply_text("Otpravleno!")


async def get_photos():
    async with httpx.AsyncClient() as client:
        r = await client.get(BIN_URL, headers={"X-Master-Key": API_KEY})
        return r.json().get("record", {}).get("photos", [])


async def save_photos(photos):
    async with httpx.AsyncClient() as client:
        await client.put(BIN_URL, headers=HEADERS, json={"photos": photos})


async def handle_photo(update, context):
    photo = update.message.photo[-1]
    caption = update.message.caption or ""
    photos = await get_photos()
    photos.append({
        "file_id": photo.file_id,
        "caption": caption,
        "date": update.message.date.strftime("%d.%m.%Y")
    })
    await save_photos(photos)
    await update.message.reply_text("Foto dobavleno! Vsego: " + str(len(photos)))


async def cmd_clear(update, context):
    await save_photos([])
    await update.message.reply_text("Galereya ochistena!")


def main():
    logger.info("Bot starting...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("sendnow", cmd_sendnow))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_daily_quote, "cron", hour=SEND_HOUR, minute=SEND_MINUTE, args=[app.bot])
    scheduler.start()
    logger.info("Scheduler started - sending every day at " + str(SEND_HOUR) + ":00 UTC")

    logger.info("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
