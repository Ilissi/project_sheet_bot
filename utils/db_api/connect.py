
import asyncio
import asyncpg
from data import config


class Database:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.pool = loop.run_until_complete(
            asyncpg.create_pool(
                user=config.PGUSER,
                password=config.PGPASSWORD,
                database=config.DATABASE,
                host=config.ip,
                port=config.PORT
            )
        )
