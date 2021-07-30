from loader import db


async def select_all_orders():
    return await db.pool.fetch('SELECT id, user_id, status, department_id FROM orders')


async def get_pays_for_worker(user_id):
    return await db.pool.fetch("SELECT id, amount, date, name_service, comment, status FROM pays WHERE user_id = $1",
                               int(user_id))


async def add_pay(id_user, amount, name_service, date, comment, department_id):
    return await db.pool.fetch(
        "INSERT INTO pays (user_id,amount,date,name_service,comment,status,department_id) VALUES ($1,$2,$3,$4,$5,$6,$7)",
        id_user, amount, date, name_service, comment, 'aprrove', department_id)


async def get_sum(value):
    return await db.pool.fetch('SELECT amount, user_id, date FROM pays WHERE department_id = $1', value)


async def get_user_pay(department_id, user_id):
    return await db.pool.fetch('SELECT user_id, amount, date, name_service, comment, department_id '
                               'FROM pays WHERE department_id = $1 AND user_id = $2', department_id, user_id)


async def select_all_pays():
    return await db.pool.fetch('SELECT id, user_id, amount, date, name_service, comment, status, department_id '
                               'FROM pays')


async def add_order(id_user, department_id):
    return await db.pool.execute(
        'INSERT INTO orders (user_id,department_id,status) VALUES ($1,$2,$3) ',
        id_user, department_id, 'worked')


