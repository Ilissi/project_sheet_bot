from loader import db


async def select_all_projects():
    return await db.pool.fetch('SELECT id, name, admin FROM projects')


async def select_in_project(value):
    return await db.pool.fetch('SELECT id, name, status FROM departments WHERE project_id = $1', int(value))


async def delete_project(project_id):
    return await db.pool.execute('DELETE FROM projects WHERE id = $1', int(project_id))


async def get_project_name(project_id):
    return await db.pool.fetch('SELECT name FROM projects WHERE id = $1', int(project_id))


async def get_project(project_id):
    return await db.pool.fetch('SELECT id, name, admin FROM projects WHERE id = $1', int(project_id))


async def get_pinned_projects(project_id):
    return await db.pool.fetch('SELECT id, name  FROM projects WHERE admin = $1', int(project_id))


async def get_free_projects():
    return await db.pool.fetch('SELECT * from projects WHERE admin = -1')


async def set_admin_in_project(id, project_id):
    return await db.pool.fetch("UPDATE projects SET admin = $1 WHERE id = $2", int(id), int(project_id))


async def add_project(name, admin):
    return await db.pool.execute('INSERT INTO projects (name,admin) VALUES ($1,$2) ', name, admin)


