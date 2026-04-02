import asyncio
import logging
import random
import httpx
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ============================================================
#  НАСТРОЙКИ — поменяй эти значения под себя
# ============================================================
BOT_TOKEN   = "8782299050:AAGhdm8O1LVXUKdvRzi4Gc4Wp7zjuq-Wl4A"   # токен от @BotFather
CHAT_ID     = "-5119427484"       # chat_id девушки (узнай через /start)
SEND_HOUR   = 9                    # час отправки (по UTC+5 Ташкент = UTC+5)
SEND_MINUTE = 0                    # минута отправки
# ============================================================

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Запасные цитаты (если интернет недоступен) ---
FALLBACK_QUOTES = [
    "Любовь — это не то, что мы находим. Любовь — это то, что мы строим вместе. 💕",
    "Настоящая любовь начинается там, где ничего не ожидают взамен. ❤️",
    "Любить — значит видеть человека таким, каким его задумал Бог. 🌸",
    "В твоих глазах я нашёл свой дом. 🏠❤️",
    "Ты — моя любимая история, которую я хочу перечитывать снова и снова. 📖💖",
    "Каждый день рядом с тобой — это подарок. 🎁",
    "Любовь — это когда счастье другого человека важнее твоего собственного. 💞",
    "Ты делаешь каждый мой день лучше просто тем, что существуешь. ✨",
]

async def fetch_love_quote() -> str:
    """Получает цитату о любви из интернета."""
    try:
        # Пробуем API цитат
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://api.quotable.io/random",
                params={"tags": "love", "maxLength": 200}
            )
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "")
                author  = data.get("author", "")
                if content:
                    return f"💌 «{content}»\n\n— {author}" if author else f"💌 «{content}»"
    except Exception as e:
        logger.warning(f"Ошибка получения цитаты из API: {e}")

    # Запасной вариант
    return random.choice(FALLBACK_QUOTES)

async def send_daily_quote(bot: Bot):
    """Отправляет ежедневную цитату о любви."""
    quote = await fetch_love_quote()
    now   = datetime.now().strftime("%d.%m.%Y")
    
    message = (
        f"🌹 *Доброе утро, моя любовь!* 🌹\n\n"
        f"{quote}\n\n"
        f"_Помни: я думаю о тебе каждый день 💕_\n"
        f"📅 {now}"
    )
    
    await bot.send_message(
        chat_id=CHAT_ID,
        text=message,
        
    )
    logger.info(f"✅ Цитата отправлена в {CHAT_ID}")

# ============================================================
#  КОМАНДЫ ДЛЯ POWERSHELL-УПРАВЛЕНИЯ
# ============================================================

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start — показывает chat_id."""
    chat_id = update.effective_chat.id
    name    = update.effective_user.first_name or "друг"
    await update.message.reply_text(
        f"👋 Привет, {name}!\n\n"
        f"🆔 Твой Chat ID: `{chat_id}`\n\n"
        f"Скопируй этот ID и вставь в CHAT_ID в настройках бота.",
        
    )

async def cmd_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /quote — отправляет цитату прямо сейчас."""
    await update.message.reply_text("💭 Ищу красивую цитату...")
    quote = await fetch_love_quote()
    await update.message.reply_text(
        f"💌 Вот твоя цитата:\n\n{quote}",
        
    )

async def cmd_send_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /sendnow — отправляет цитату девушке прямо сейчас."""
    bot = context.bot
    await update.message.reply_text("💌 Отправляю цитату...")
    await send_daily_quote(bot)
    await update.message.reply_text(f"✅ Цитата отправлена на chat_id: {CHAT_ID}")

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /status — показывает статус бота."""
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    await update.message.reply_text(
        f"🤖 *Статус бота*\n\n"
        f"✅ Бот работает\n"
        f"🕐 Время сейчас: {now}\n"
        f"📬 Получатель: `{CHAT_ID}`\n"
        f"⏰ Время отправки: {SEND_HOUR:02d}:{SEND_MINUTE:02d} (UTC)",
        
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help — список команд."""
    await update.message.reply_text(
        "📋 *Список команд:*\n\n"
        "/start — показать твой Chat ID\n"
        "/quote — получить случайную цитату о любви\n"
        "/sendnow — отправить цитату девушке прямо сейчас\n"
        "/status — статус бота и расписание\n"
        "/help — этот список\n\n"
        f"⏰ Автоматическая отправка: каждый день в {SEND_HOUR:02d}:{SEND_MINUTE:02d} UTC",
        
    )

# ============================================================
#  ЗАПУСК
# ============================================================

def main():
    logger.info("🚀 Запуск бота...")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Регистрируем команды
    app.add_handler(CommandHandler("start",   cmd_start))
    app.add_handler(CommandHandler("quote",   cmd_quote))
    app.add_handler(CommandHandler("sendnow", cmd_send_now))
    app.add_handler(CommandHandler("status",  cmd_status))
    app.add_handler(CommandHandler("help",    cmd_help))

    # Планировщик ежедневной отправки
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_daily_quote,
        trigger="cron",
        hour=SEND_HOUR,
        minute=SEND_MINUTE,
        args=[app.bot],
        id="daily_love_quote"
    )
    scheduler.start()
    logger.info(f"⏰ Планировщик запущен — отправка каждый день в {SEND_HOUR:02d}:{SEND_MINUTE:02d} UTC")

    logger.info("✅ Бот запущен! Нажми Ctrl+C для остановки.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
