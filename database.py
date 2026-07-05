import asyncpg
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

async def create_pool():
    return await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )