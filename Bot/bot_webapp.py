import logging
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "8782299050:AAGhdm8O1LVXUKdvRzi4Gc4Wp7zjuq-Wl4A"

# ВАЖНО: замени на ссылку где будет лежать webapp.html
# Например после загрузки на GitHub Pages:
# WEBAPP_URL = "https://abduxalilov717-sketch.github.io/Love-bot/webapp.html"
WEBAPP_URL = "https://abduxalilov717-sketch.github.io/Love-bot/webapp.html"

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💕 Цитата о любви", web_app=WebAppInfo(url="https://abduxalilov717-sketch.github.io/Love-bot/webapp.html"))],
        [InlineKeyboardButton("🧠 Викторина про меня", web_app=WebAppInfo(url="https://abduxalilov717-sketch.github.io/Love-bot/quiz.html"))],
        [InlineKeyboardButton("📸 Наши фото", web_app=WebAppInfo(url="https://abduxalilov717-sketch.github.io/Love-bot/photos.html"))],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Привет! Выбери раздел ниже 💕",
        reply_markup=reply_markup
    )

async def cmd_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📅 Наши даты", web_app=WebAppInfo(url=WEBAPP_URL))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Открываю календарь...", reply_markup=reply_markup)

def main():
    logger.info("Bot starting...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("calendar", cmd_calendar))
    logger.info("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
    if __name__ == "__main__":
    main()
