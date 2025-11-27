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
rows = await cur.fetchall()
        return [dict(id=r[0], creator_id=r[1], amount=r[2], creator_choice=r[3]) for r in rows]

async def create_match(creator_id: int, amount: int, creator_choice: int) -> int:
    if amount <= 0:
        raise ValueError("amount must be positive")
    async with aiosqlite.connect(DB) as db:
        await db.execute("BEGIN;")
        await db.execute("UPDATE users SET balance = balance - ? WHERE id=? AND balance>=?;", (amount, creator_id, amount))
        cur = await db.execute("SELECT changes();")
        changes = (await cur.fetchone())[0]
        if changes == 0:
            await db.execute("ROLLBACK;")
            raise ValueError("insufficient funds")
        ins = await db.execute("INSERT INTO matches(creator_id, amount, creator_choice, status) VALUES(?,?,?, 'open');", (creator_id, amount, creator_choice))
        await db.commit()
        return ins.lastrowid

async def join_match(taker_id: int, match_id: int, taker_choice: int):
    async with aiosqlite.connect(DB) as db:
        await db.execute("BEGIN;")
        cur = await db.execute("SELECT amount, creator_id, creator_choice FROM matches WHERE id=? AND status='open';", (match_id,))
        row = await cur.fetchone()
        if not row:
            await db.execute("ROLLBACK;")
            raise ValueError("match not available")
        amount, creator_id, creator_choice = row
        if taker_id == creator_id:
            await db.execute("ROLLBACK;")
            raise ValueError("creator cannot join own match")
        await db.execute("UPDATE users SET balance = balance - ? WHERE id=? AND balance>=?;", (amount, taker_id, amount))
        cur2 = await db.execute("SELECT changes();")
        changed = (await cur2.fetchone())[0]
        if changed == 0:
            await db.execute("ROLLBACK;")
            raise ValueError("insufficient funds")
        await db.execute("UPDATE matches SET taker_id=?, taker_choice=?, status='closed' WHERE id=? AND status='open';", (taker_id, taker_choice, match_id))
        cur3 = await db.execute("SELECT changes();")
        claimed = (await cur3.fetchone())[0]
        if claimed == 0:
            await db.execute("UPDATE users SET balance = balance + ? WHERE id=?;", (amount, taker_id))
            await db.execute("ROLLBACK;")
            raise ValueError("match already taken")
        result = secrets.randbelow(6) + 1
        commission = int(amount * COMMISSION / 100)
        if creator_choice == result:
            winner = creator_id
        else:
            winner = taker_id
        payout = amount * 2 - commission
        await db.execute("UPDATE users SET balance = balance + ? WHERE id=?;", (payout, winner))
        await db.execute("UPDATE owner_account SET balance = balance + ? WHERE id=1;", (commission,))
        await db.execute("UPDATE matches SET status='finished' WHERE id=?;", (match_id,))
        await db.execute("INSERT INTO history(match_id, winner_id, amount, commission) VALUES(?,?,?,?);", (match_id, winner, amount, commission))
        await db.commit()
        return {"result": result, "winner": winner, "commission": commission}
