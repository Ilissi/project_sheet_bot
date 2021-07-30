from loader import db


async def update_status(id_telegram, status):
    return await db.pool.fetch('UPDATE orders SET status = $1 WHERE user_id = $2', status, id_telegram)


async def select_all_users():
    return await db.pool.fetch('SELECT id, id_telegram, nickname, permissions FROM users')


async def select_user(id_telegram):
    return await db.pool.fetch('SELECT id_telegram, nickname, permissions FROM users WHERE id_telegram = $1',
                               int(id_telegram))


async def select_admins():
    return await db.pool.fetch("SELECT id, id_telegram, nickname FROM users WHERE permissions = 'admin'")


async def delete_user(id_telegram):
    return await db.pool.execute('DELETE FROM users WHERE id = $1', int(id_telegram))


async def get_id_telegram(id_telegram):
    return await db.pool.fetch('SELECT id_telegram, nickname, permissions FROM users WHERE id = $1', int(id_telegram))


async def get_user_nickname(id_telegram):
    return await db.pool.fetch('SELECT nickname FROM users WHERE id_telegram = $1', int(id_telegram))


async def get_archive_users():
    return await db.pool.fetch("SELECT id, user_id, department_id FROM orders WHERE status = 'archive'")


async def get_worker(user_id):
    return await db.pool.fetch("SELECT id, status, department_id FROM orders WHERE user_id = $1", int(user_id))


async def set_status_worker(user_id, status):
    return await db.pool.fetch("UPDATE orders SET status = $1 WHERE user_id = $2", status, int(user_id))


async def is_user(id_telegram):
    res = await db.pool.fetch(f'SELECT id, nickname, permissions FROM users WHERE id_telegram = $1', int(id_telegram))
    return res[0]['permissions'] == 'user' if len(res) != 0 else False


async def is_admin(id_telegram):
    res = await db.pool.fetch(f'SELECT id, nickname, permissions FROM users WHERE id_telegram = $1', int(id_telegram))
    return res[0]['permissions'] == 'admin' if len(res) != 0 else False


async def get_user_id(value):
    return await db.pool.fetch('SELECT user_id FROM pays WHERE department_id = $1', value)


async def get_user(value):
    return await db.pool.fetch('SELECT id, nickname FROM users WHERE id_telegram = $1', value)


async def get_username(value):
    return await db.pool.fetch('SELECT id,id_telegram,nickname FROM users WHERE id = $1', value)


async def add_user(id_telegram, nickname, permissions):
    return await db.pool.execute('INSERT INTO users (id_telegram,nickname,permissions) VALUES ($1,$2,$3) ',
                                 id_telegram, nickname, permissions)


async def select_workers_in_department(id):
    return await db.pool.fetch('SELECT id, user_id, status FROM orders WHERE department_id = $1', int(id))





