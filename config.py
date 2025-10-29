# config.py
import os
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
SPY_GROUP_ID = int(os.getenv("SPY_GROUP_ID", 0))
DEVELOPER_USERNAME = os.getenv("DEVELOPER_USERNAME", "@NEOBLADE71")
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "https://t.me/NEO_SUPPORT_CHANNEL")
SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "https://t.me/NEON_SUPPORT_GROUP")
DB_PASSWORD = os.getenv("DB_PASSWORD", "defaultpass")
DEFAULT_AI = os.getenv("DEFAULT_AI", "openai").lower()
MAX_HISTORY = int(os.getenv("MAX_HISTORY", 10))
RATE_LIMIT = int(os.getenv("RATE_LIMIT", 5))
DB_PATH = os.getenv("DB_PATH", "bot.db")