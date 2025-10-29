# database.py
from pysqlcipher3 import dbapi2 as sqlite
from config import DB_PATH, DB_PASSWORD

def get_conn():
    conn = sqlite.connect(DB_PATH)
    conn.execute(f"PRAGMA key = '{DB_PASSWORD}'")
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, verified INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history (id INTEGER PRIMARY KEY, user_id INTEGER, role TEXT, content TEXT, timestamp TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY, user_id INTEGER, message TEXT, timestamp TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS banned (id INTEGER PRIMARY KEY, user_id INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS spam_timers (user_id INTEGER PRIMARY KEY, expiry REAL)''')
    conn.commit(); conn.close()

def add_user(user_id: int, username: str):
    conn = get_conn(); c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)", (user_id, username))
    conn.commit(); conn.close()

def verify_user(user_id: int):
    conn = get_conn(); c = conn.cursor()
    c.execute("UPDATE users SET verified = 1 WHERE id = ?", (user_id,))
    conn.commit(); conn.close()

def is_verified(user_id: int) -> bool:
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT verified FROM users WHERE id = ?", (user_id,))
    res = c.fetchone(); conn.close()
    return res and res[0] == 1

def add_history(user_id: int, role: str, content: str):
    conn = get_conn(); c = conn.cursor()
    c.execute("INSERT INTO chat_history (user_id, role, content, timestamp) VALUES (?, ?, ?, datetime('now'))", (user_id, role, content))
    conn.commit(); conn.close()

def get_history(user_id: int, limit: int = 10):
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT role, content FROM chat_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?;", (user_id, limit))
    history = [{"role": r[0], "content": r[1]} for r in c.fetchall()][::-1]
    conn.close(); return history

def add_feedback(user_id: int, message: str):
    conn = get_conn(); c = conn.cursor()
    c.execute("INSERT INTO feedback (user_id, message, timestamp) VALUES (?, ?, datetime('now'))", (user_id, message))
    conn.commit(); conn.close()

def get_stats():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users"); users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM chat_history"); msgs = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM feedback"); fb = c.fetchone()[0]
    conn.close(); return {"users": users, "messages": msgs, "feedback": fb}

def get_all_user_ids():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT id FROM users"); ids = [r[0] for r in c.fetchall()]
    conn.close(); return ids

def ban_user(user_id: int):
    conn = get_conn(); c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO banned (user_id) VALUES (?)", (user_id,))
    conn.commit(); conn.close()

def unban_user(user_id: int):
    conn = get_conn(); c = conn.cursor()
    c.execute("DELETE FROM banned WHERE user_id = ?", (user_id,))
    conn.commit(); conn.close()

def is_banned(user_id: int) -> bool:
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT 1 FROM banned WHERE user_id = ?", (user_id,))
    res = c.fetchone(); conn.close()
    return res is not None

def set_spam_timer(user_id: int, expiry: float):
    conn = get_conn(); c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO spam_timers (user_id, expiry) VALUES (?, ?)", (user_id, expiry))
    conn.commit(); conn.close()

def get_spam_timer(user_id: int) -> float:
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT expiry FROM spam_timers WHERE user_id = ?", (user_id,))
    res = c.fetchone(); conn.close()
    return res[0] if res else 0