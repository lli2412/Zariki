import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
START_BALANCE = int(os.getenv("START_BALANCE", "100"))
COMMISSION = int(os.getenv("COMMISSION", "5"))  # percent
DATABASE_URL = os.getenv("DATABASE_URL", "data/game.db")
