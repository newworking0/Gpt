# utils.py
import re, time, psutil, logging
from datetime import datetime, timedelta
from collections import deque
from config import ADMIN_IDS, RATE_LIMIT
from database import get_conn, is_verified, is_banned, ban_user

start_time = time.time()
logger = logging.getLogger(__name__)

def mask_sensitive(text: str) -> str:
    patterns = [
        r'(password|pwd|pass|token|key|sk-)[^,\s]+',
        r'[\w\.-]+@[\w\.-]+\.\w+'
    ]
    for p in patterns:
        text = re.sub(p, lambda m: m.group(0)[0] + '[MASKED]', text, flags=re.IGNORECASE)
    return text

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def rate_limit_check(user_id: int, limits: dict) -> bool:
    now = datetime.now()
    if user_id not in limits:
        limits[user_id] = deque(maxlen=RATE_LIMIT + 1)
    limits[user_id].append(now)
    recent = [t for t in limits[user_id] if now - t < timedelta(minutes=1)]
    if len(recent) > RATE_LIMIT:
        return True
    return False

def get_bot_status() -> str:
    uptime = time.time() - start_time
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM chat_history")
    msgs = c.fetchone()[0]
    conn.close()
    return f"Uptime: {uptime / 3600:.2f}h\nUsers: {users}\nMessages: {msgs}\nCPU: {cpu}%\nRAM: {mem}%"