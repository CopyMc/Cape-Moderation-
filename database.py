import aiosqlite
import datetime
from config import WARN_LIMIT

class Database:
    def __init__(self):
        self.db_path = "moderation.db"
    
    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:

            await db.execute('''
                CREATE TABLE IF NOT EXISTS warns (
                    warn_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    moderator_id INTEGER,
                    reason TEXT,
                    timestamp TIMESTAMP,
                    guild_id INTEGER
                )
            ''')
            
  
            await db.execute('''
                CREATE TABLE IF NOT EXISTS mutes (
                    mute_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    moderator_id INTEGER,
                    reason TEXT,
                    duration INTEGER,
                    timestamp TIMESTAMP,
                    guild_id INTEGER
                )
            ''')
            

            await db.execute('''
                CREATE TABLE IF NOT EXISTS bans (
                    ban_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    moderator_id INTEGER,
                    reason TEXT,
                    timestamp TIMESTAMP,
                    guild_id INTEGER
                )
            ''')
            
            await db.commit()
    
    async def add_warn(self, user_id: int, moderator_id: int, reason: str, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                '''INSERT INTO warns (user_id, moderator_id, reason, timestamp, guild_id)
                VALUES (?, ?, ?, ?, ?)''',
                (user_id, moderator_id, reason, datetime.datetime.now().isoformat(), guild_id)
            )
            await db.commit()
    
    async def get_warns(self, user_id: int, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM warns WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            )
            return await cursor.fetchall()
    
    async def clear_warns(self, user_id: int, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM warns WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            )
            await db.commit()
    
    async def add_mute(self, user_id: int, moderator_id: int, reason: str, duration: int, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                '''INSERT INTO mutes (user_id, moderator_id, reason, duration, timestamp, guild_id)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (user_id, moderator_id, reason, duration, datetime.datetime.now().isoformat(), guild_id)
            )
            await db.commit()
    
    async def add_ban(self, user_id: int, moderator_id: int, reason: str, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                '''INSERT INTO bans (user_id, moderator_id, reason, timestamp, guild_id)
                VALUES (?, ?, ?, ?, ?)''',
                (user_id, moderator_id, reason, datetime.datetime.now().isoformat(), guild_id)
            )
            await db.commit()

db = Database()