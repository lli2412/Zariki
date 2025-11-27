import aiosqlite
from .settings import DATABASE_URL, COMMISSION, START_BALANCE
import secrets
from typing import List, Dict

DB = DATABASE_URL

async def ensure_user(user_id: int, start_balance: int = START_BALANCE):
    async with aiosqlite.connect(DB) as db:
        await db.execute("INSERT OR IGNORE INTO users(id, balance) VALUES(?, ?);", (user_id, start_balance))
        await db.commit()

async def get_balance(user_id: int) -> int:
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT balance FROM users WHERE id=?;", (user_id,))
        row = await cur.fetchone()
        return row[0] if row else 0

async def list_open_matches() -> List[Dict]:
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT id, creator_id, amount, creator_choice FROM matches WHERE status='open';")
