# -*- coding: utf-8 -*-
import logging
import json
import os
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8782299050:AAGhdm8O1LVXUKdvRzi4Gc4Wp7zjuq-Wl4A"
PHOTOS_FILE = "photos.json"
WEBAPP_URL = "https://abduxalilov717-sketch.github.io/Love-bot/photos.html"

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def load_photos():
    if os.path.exists(PHOTOS_FILE):
        with open(PHOTOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_photos(photos):
    with open(PHOTOS_FILE, "w", encoding="utf-8") as f:
        json.dump(photos, f, ensure_ascii=False, indent=2)

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

async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photos = load_photos()
    if not photos:
        await update.message.reply_text("Нет фото. Отправь мне фото чтобы добавить!")
        return
    await update.message.reply_text(f"В галерее {len(photos)} фото 📸")

async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_photos([])
    await update.message.reply_text("Галерея очищена!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]  # берем лучшее качество
    file_id = photo.file_id
    caption = update.message.caption or ""

    photos = load_photos()
    photos.append({
        "file_id": file_id,
        "caption": caption,
        "date": update.message.date.strftime("%d.%m.%Y")
    })
    save_photos(photos)

    keyboard = [[InlineKeyboardButton("💕 Посмотреть галерею", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_text(
        f"Фото добавлено в галерею! Всего фото: {len(photos)} 📸",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    logger.info(f"Photo added: {file_id}, caption: {caption}")

def main():
    logger.info("Bot starting...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("photos", cmd_photos))
    app.add_handler(CommandHandler("list", cmd_list))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    logger.info("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
