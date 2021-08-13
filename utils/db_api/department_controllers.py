from loader import db


async def get_departments(value):
    return await db.pool.fetch('SELECT id, project_id, status, department_name FROM departments WHERE project_id = $1',
                               value)  # sheet_id


async def get_admin_departments(value, telegram_id):
    return await db.pool.fetch('SELECT id, project_id, status, department_name, settings FROM departments '
                               'WHERE project_id = $1 AND admin_id = $2', value, telegram_id)


async def get_departments_for_add_admin(value):
    return await db.pool.fetch("SELECT id, project_id, status, department_name FROM departments WHERE project_id = $1", value)


async def get_departments_for_add_user(value):
    return await db.pool.fetch("SELECT id, project_id, status, department_name FROM departments WHERE project_id = $1 "
                               "AND status='open'", value)


async def get_department_to_id(value):
    return await db.pool.fetch('SELECT id, project_id, department_name, status FROM departments WHERE id = $1', value)


async def get_departments_pay(department_id):
    return await db.pool.fetch('SELECT user_id, amount, date, name_service, comment, department_id '
                               'FROM pays WHERE department_id = $1 ', department_id)


async def select_all_departments():
    return await db.pool.fetch('SELECT id, project_id, department_name, status FROM departments')


async def add_department(id_project, name):
    return await db.pool.execute('INSERT INTO departments (project_id,department_name,status) VALUES ($1,$2,$3) ', id_project,
                                 name, 'open')


async def set_dep_status(department_id, status):
    return await db.pool.fetch("UPDATE departments SET status = $1 WHERE id = $2", status, int(department_id))


async def delete_department(id):
    return await db.pool.execute('DELETE FROM departments WHERE id = $1', int(id))


async def get_pinned_departments_by_project(project_id, department_id):
    return await db.pool.fetch('SELECT id, project_id, department_name, status FROM departments '
                               'WHERE project_id = $1 AND id = $2 ', project_id, department_id)
