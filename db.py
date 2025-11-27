import aiosqlite
import asyncio
import os
from .settings import DATABASE_URL

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY,
  balance INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS matches(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  creator_id INTEGER NOT NULL,
  creator_choice INTEGER NOT NULL,
  taker_id INTEGER,
  taker_choice INTEGER,
  amount INTEGER NOT NULL,
  status TEXT NOT NULL, -- open/closed/finished
  FOREIGN KEY(creator_id) REFERENCES users(id),
  FOREIGN KEY(taker_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS history(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  match_id INTEGER,
  winner_id INTEGER,
  amount INTEGER,
  commission INTEGER,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS owner_account(
  id INTEGER PRIMARY KEY,
  balance INTEGER NOT NULL
);
"""

async def init_db(db_path: str = None):
    db_path = db_path or DATABASE_URL
    dirname = os.path.dirname(db_path)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)
    async with aiosqlite.connect(db_path) as db:
        await db.executescript(SCHEMA)
        # ensure owner_account row exists
        await db.execute("INSERT OR IGNORE INTO owner_account(id, balance) VALUES(1, 0);")
        await db.commit()

if __name__ == "__main__":
    import sys
    path = None
    if len(sys.argv) > 1 and sys.argv[1] in ("--init",):
        path = None
    asyncio.run(init_db(path))
    print("DB initialized at", path or DATABASE_URL)
