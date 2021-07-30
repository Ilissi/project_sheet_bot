from loader import db, dp
from utils.db_api import create_table
import middlewares, filters, handlers
from aiogram import executor
from utils.notify_admins import on_startup_notify

import asyncio

async def on_startup(dp):

    await on_startup_notify(dp)
    await create_table.create_table_users()
    await create_table.create_table_project()
    await create_table.create_table_departments()
    await create_table.create_table_orders()
    await create_table.create_table_pays()
    await create_table.create_table_spread_id()
    await create_table.create_table_spreadsheet_id()



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    executor.start_polling(dp, on_startup=on_startup, loop=loop)
