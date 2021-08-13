from loader import db


async def select_all_orders():
    return await db.pool.fetch('SELECT id, user_id, status, department_id FROM orders')


async def get_pays_for_worker(user_id):
    return await db.pool.fetch("SELECT id, amount, date, name_service, comment, status FROM pays WHERE user_id = $1",
                               int(user_id))


async def add_pay_for_user(id_user, amount, name_service, date, comment, status, department_id):
    return await db.pool.fetch(
        "INSERT INTO pays (user_id,amount,date,name_service,comment,status,department_id) VALUES ($1,$2,$3,$4,$5,$6,$7) RETURNING *",
        id_user, amount, date, name_service, comment, status, department_id)


async def get_sum(value):
    return await db.pool.fetch('SELECT amount, user_id, date FROM pays WHERE department_id = $1', value)


async def get_user_pay(department_id, user_id):
    return await db.pool.fetch('SELECT user_id, amount, date, name_service, comment, status, department_id '
                               'FROM pays WHERE department_id = $1 AND user_id = $2', department_id, user_id)


async def select_all_pays():
    return await db.pool.fetch('SELECT id, user_id, amount, date, name_service, comment, status, department_id '
                               'FROM pays')


async def add_order(id_user, department_id):
    return await db.pool.execute(
        'INSERT INTO orders (user_id,department_id,status) VALUES ($1,$2,$3) ',
        id_user, department_id, 'worked')


async def get_department_by_user_id(department_id, user_id):
    return await db.pool.fetch('SELECT FROM orders WHERE department_id=$1 AND user_id=$2', department_id, user_id)


async def set_dep_admin(department_id, telegram_id):
    return await db.pool.fetch('INSERT INTO orders (user_id,department_id,status) VALUES ($1,$2,$3)',
                               telegram_id, department_id, 'admin')


async def get_dep_admin(department_id, telegram_id):
    return await db.pool.fetch('SELECT id FROM orders WHERE department_id = $1 AND user_id = $2',
                               department_id, telegram_id,)


async def get_departments_from_orders(user_id):
    return await db.pool.fetch('SELECT id, user_id, status, department_id FROM orders WHERE user_id = $1', user_id)


async def delete_dep_admin(department_id, telegram_id):
    return await db.pool.fetch('DELETE FROM orders WHERE department_id = $1 AND user_id = $2', department_id, telegram_id)


async def get_department_admin(department_id):
    return await db.pool.fetch('SELECT user_id FROM orders WHERE department_id = $1 and status = $2', department_id, 'admin')


async def update_status_pay(pay_id, status_message):
    return await db.pool.execute('UPDATE pays SET status = $1 WHERE id = $2', status_message, pay_id)


async def get_pay_by_id(pay_id):
    return await db.pool.fetch('SELECT id, user_id, amount, date, name_service, comment, status, department_id '
                               'FROM pays WHERE id = $1', pay_id)

