# -*- coding: utf-8 -*-
import logging
import json
import httpx
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN  = "8782299050:AAGhdm8O1LVXUKdvRzi4Gc4Wp7zjuq-Wl4A"
WEBAPP_URL = "https://abduxalilov717-sketch.github.io/Love-bot/photos.html"
BIN_ID     = "69cf7db6856a682189f67635"
API_KEY    = "$2a$10$vrr04luN8fRaLFxvBr09EOjRRIBm75kKW1EQJY7SBhElJaa1KZXUu"
BIN_URL    = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS    = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_photos():
    async with httpx.AsyncClient() as client:
        r = await client.get(BIN_URL, headers={"X-Master-Key": API_KEY})
        data = r.json()
        return data.get("record", {}).get("photos", [])

async def save_photos(photos):
    async with httpx.AsyncClient() as client:
        await client.put(BIN_URL, headers=HEADERS, json={"photos": photos})

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("💕 Наши фото", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_text(
        "Привет! Отправь мне фото и я добавлю его в нашу галерею 📸\n\n"
        "Можешь добавить подпись — просто напиши текст вместе с фото.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def cmd_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📸 Открыть галерею", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_text("Открываю нашу галерею...", reply_markup=InlineKeyboardMarkup(keyboard))

async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await save_photos([])
    await update.message.reply_text("Галерея очищена!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file_id = photo.file_id
    caption = update.message.caption or ""

    photos = await get_photos()
    photos.append({
        "file_id": file_id,
        "caption": caption,
        "date": update.message.date.strftime("%d.%m.%Y")
    })
    await save_photos(photos)

    keyboard = [[InlineKeyboardButton("💕 Посмотреть галерею", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_text(
        f"Фото добавлено! Всего фото: {len(photos)} 📸",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    logger.info("Bot starting...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("photos", cmd_photos))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    logger.info("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
