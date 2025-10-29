# main.py
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import TELEGRAM_TOKEN
from handlers import *
from database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    init_db()
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ai", switch_ai))
    app.add_handler(CommandHandler("imagine", imagine))
    app.add_handler(CommandHandler("feedback", feedback))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("ban", ban_user_cmd))
    app.add_handler(CommandHandler("unban", unban_user_cmd))
    app.add_handler(CommandHandler("status", status_handler))
    app.add_handler(CommandHandler("verify", verify_handler))
    app.add_handler(CommandHandler("health", health_handler))
    app.add_handler(CommandHandler("getid", get_id))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new))

    # Buttons
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(ai_chat|imagine|support|developer)$"))
    app.add_handler(CallbackQueryHandler(button_callback, pattern="^joined_check$"))

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()