from loader import db


async def get_spreadsheet():
    return await db.pool.fetch('SELECT spreadsheet_id FROM spread')


async def update_spreadsheet(value):
    return await db.pool.execute('INSERT INTO spread (spreadsheet_id) VALUES ($1)', value)


async def insert_spread(sheet_id, sheet_title, page, project_id):
    return await db.pool.execute('INSERT INTO spread_project (sheet_id, sheet_title, page, project_id) '
                                 'VALUES ($1, $2, $3, $4)',
                                 sheet_id, sheet_title, page, project_id)


async def get_spread(project_id):
    return await db.pool.fetch('SELECT sheet_id, sheet_title, page FROM spread_project '
                               'WHERE project_id = $1', project_id)


async def get_spread_page(project_id, page):
    return await db.pool.fetch('SELECT sheet_id, sheet_title, page FROM spread_project '
                               'WHERE project_id = $1 AND page = $2', project_id, page)
