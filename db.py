import aiosqlite

async def creat_table():
    async with aiosqlite.connect('alerterbot.sql') as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users(tg_id INT, coin TEXT, choice TEXT, percent REAL, start_rate REAL, in_process INT)")
        await db.commit()

async def select_by_users_id(tg_id):
    async with aiosqlite.connect('alerterbot.sql') as db:
        async with db.execute("SELECT * FROM users WHERE tg_id=?", (tg_id,)) as cursor:
            return await cursor.fetchall()
            
async def add_info(parameters: tuple, values: tuple):
    async with aiosqlite.connect('alerterbot.sql') as db:
        count = '?' + ', ?' * (len(parameters) - 1)
        await db.execute(f"INSERT INTO users {parameters} VALUES ({count})", values)
        await db.commit()

async def get_active_reminders():
    async with aiosqlite.connect('alerterbot.sql') as db:
        async with db.execute("SELECT * FROM users WHERE in_process = 1") as curs:
            return await curs.fetchall()
    
async def set_status(rate):
    async with aiosqlite.connect('alerterbot.sql') as db:
        await db.execute("UPDATE users SET in_process = 0 WHERE in_process = 1 AND start_rate = ?", (rate, ))
        db.commit()