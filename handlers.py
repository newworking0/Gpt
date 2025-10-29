# handlers.py
import os, random, logging, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import *
from ai_engine import *
from utils import *
from spy_logger import log_to_spy_group
from config import *

current_model = DEFAULT_AI
rate_limits = {}
captcha_challenges = {}
logger = logging.getLogger(__name__)

# ========================
# SUPPORT JOIN CHECK
# ========================
async def require_support_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        channel = await context.bot.get_chat_member("@NEO_SUPPORT_CHANNEL", user_id)
        group = await context.bot.get_chat_member("@NEON_SUPPORT_GROUP", user_id)
        if channel.status in ["member", "administrator", "creator"] and group.status in ["member", "administrator", "creator"]:
            return True
    except: pass
    keyboard = [
        [InlineKeyboardButton("Join Channel", url=SUPPORT_CHANNEL)],
        [InlineKeyboardButton("Join Group", url=SUPPORT_GROUP)],
        [InlineKeyboardButton("I Joined!", callback_data="joined_check")]
    ]
    await update.message.reply_text(
        "Please join our support channel & group first!\n"
        "Then click 'I Joined!'",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return False

# ========================
# CALLBACK QUERY
# ========================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "joined_check":
        if await require_support_join(update, context):
            await query.edit_message_text("Verified! You can use the bot now.")
        else:
            await query.edit_message_text("Still not joined! Please join both.")

# ========================
# START WITH BUTTONS
# ========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username or "Unknown")
    keyboard = [
        [InlineKeyboardButton("AI Chat", callback_data="ai_chat")],
        [InlineKeyboardButton("Generate Image", callback_data="imagine")],
        [InlineKeyboardButton("Support", callback_data="support")],
        [InlineKeyboardButton("Developer", callback_data="developer")]
    ]
    await update.message.reply_text(
        f"Welcome {user.first_name}!\n"
        "Choose an option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await log_to_spy_group(update, context)

# ========================
# BUTTON ACTIONS
# ========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "ai_chat":
        await query.edit_message_text("Send any message to chat with AI!")
    elif data == "imagine":
        await query.edit_message_text("Send: /imagine <prompt>")
    elif data == "support":
        keyboard = [
            [InlineKeyboardButton("Channel", url=SUPPORT_CHANNEL)],
            [InlineKeyboardButton("Group", url=SUPPORT_GROUP)]
        ]
        await query.edit_message_text("Support Links:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "developer":
        dev_text = (
            f"Meet the genius behind this bot – {DEVELOPER_USERNAME}!\n\n"
            "A master coder, AI wizard, and Telegram automation expert with 5+ years of experience. "
            "He has built 50+ bots used by 100K+ users. His code is clean, secure, and lightning fast. "
            "From AI chatbots to spy systems, payment bots to auto-posters – he does it all!\n\n"
            "Want your own custom bot? DM him now: {DEVELOPER_USERNAME}\n"
            "Any idea, any feature – he’ll build it in 24 hours!"
        )
        await query.edit_message_text(dev_text)
    await log_to_spy_group(update, context)

# ========================
# ANTI-SPAM SYSTEM
# ========================
async def anti_spam_check(user_id: int, chat_type: str):
    now = asyncio.get_event_loop().time()
    if user_id not in rate_limits:
        rate_limits[user_id] = []
    rate_limits[user_id].append(now)
    rate_limits[user_id] = [t for t in rate_limits[user_id] if now - t < 10]
    if len(rate_limits[user_id]) > 5:
        if chat_type == "private":
            ban_user(user_id)
            return "You are permanently banned for spamming."
        else:
            expiry = now + 600
            set_spam_timer(user_id, expiry)
            return "You are muted for 10 minutes for spamming."
    return None

# ========================
# CHAT HANDLER
# ========================
async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type

    # Anti-spam
    spam_msg = await anti_spam_check(user_id, chat_type)
    if spam_msg:
        await update.message.reply_text(spam_msg)
        await log_to_spy_group(update, context)
        return

    # Support join
    if not await require_support_join(update, context):
        return

    # Verified
    if not is_verified(user_id) and not is_admin(user_id):
        await update.message.reply_text("Please /verify first.")
        return

    text = update.message.text
    history = get_history(user_id, MAX_HISTORY)
    reply = await get_ai_reply(text, history, current_model)
    add_history(user_id, "user", text)
    add_history(user_id, "assistant", reply)
    await update.message.reply_text(reply)
    await log_to_spy_group(update, context)