from loader import db


async def select_all_projects():
    return await db.pool.fetch('SELECT id, project_name FROM projects')


async def select_in_project(value):
    return await db.pool.fetch('SELECT id, department_name, status FROM departments WHERE project_id = $1', int(value))


async def delete_project(project_id):
    return await db.pool.execute('DELETE FROM projects WHERE id = $1', int(project_id))


async def get_project_name(project_id):
    return await db.pool.fetch('SELECT project_name FROM projects WHERE id = $1', int(project_id))


async def get_project(project_id):
    return await db.pool.fetch('SELECT id, project_name FROM projects WHERE id = $1', int(project_id))


async def get_pinned_projects(project_id):
    return await db.pool.fetch('SELECT id, project_name FROM projects WHERE admin = $1', int(project_id))


async def set_admin_in_project(id, project_id):
    return await db.pool.fetch("UPDATE projects SET admin = $1 WHERE id = $2", int(id), int(project_id))


async def add_project(name):
    return await db.pool.execute('INSERT INTO projects (project_name) VALUES ($1) ', name)


async def clear_admin_project(telegram_id):
    return await db.pool.fetch('UPDATE projects SET project_name = -1 WHERE project_name = $1', telegram_id)


