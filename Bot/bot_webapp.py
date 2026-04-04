# -*- coding: utf-8 -*-
import logging
import httpx
import json
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN  = "8782299050:AAGhdm8O1LVXUKdvRzi4Gc4Wp7zjuq-Wl4A"
BASE_URL   = "https://abduxalilov717-sketch.github.io/Love-bot"
BIN_ID     = "69cf7db6856a682189f67635"
API_KEY    = "$2a$10$vrr04luN8fRaLFxvBr09EOjRRIBm75kKW1EQJY7SBhElJaa1KZXUu"
BIN_URL    = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS    = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💌 Цитата о любви", web_app=WebAppInfo(url=f"{BASE_URL}/webapp.html"))],
        [InlineKeyboardButton("🧠 Викторина про меня", web_app=WebAppInfo(url=f"{BASE_URL}/quiz.html"))],
        [InlineKeyboardButton("📸 Наши фото", web_app=WebAppInfo(url=f"{BASE_URL}/photos.html"))],
    ])

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет, моя любовь! 💕\n\nВыбери что открыть:",
        reply_markup=main_keyboard()
    )

async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выбери:", reply_markup=main_keyboard())

async def get_photos():
    async with httpx.AsyncClient() as client:
        r = await client.get(BIN_URL, headers={"X-Master-Key": API_KEY})
        return r.json().get("record", {}).get("photos", [])

async def save_photos(photos):
    async with httpx.AsyncClient() as client:
        await client.put(BIN_URL, headers=HEADERS, json={"photos": photos})

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    caption = update.message.caption or ""
    photos = await get_photos()
    photos.append({
        "file_id": photo.file_id,
        "caption": caption,
        "date": update.message.date.strftime("%d.%m.%Y")
    })
    await save_photos(photos)
    await update.message.reply_text(
        f"Фото добавлено в галерею! Всего: {len(photos)} 📸",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📸 Посмотреть", web_app=WebAppInfo(url=f"{BASE_URL}/photos.html"))
        ]])
    )

async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await save_photos([])
    await update.message.reply_text("Галерея очищена!")

def main():
    logger.info("Bot starting...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    logger.info("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
