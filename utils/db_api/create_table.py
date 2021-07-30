from loader import db


async def create_table_users():
    sql = """ 
    CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    id_telegram INT NOT NULL,
    nickname VARCHAR(255) NOT NULL,
    permissions VARCHAR(255) NOT NULL,
    UNIQUE (id_telegram))
    """
    await db.pool.execute(sql)


async def create_table_project():
    sql = """ 
    CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    admin INT NOT NULL,
    UNIQUE (name))
    """
    await db.pool.execute(sql)


async def create_table_departments():
    sql = """ 
    CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY ,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(255) NOT NULL,
    UNIQUE (name))
    """
    await db.pool.execute(sql)


async def create_table_orders():
    sql = """ 
    CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id_telegram) ON DELETE CASCADE,
    status VARCHAR(255) NOT NULL,
    department_id INTEGER REFERENCES departments(id) ON DELETE CASCADE)
    """
    await db.pool.execute(sql)


async def create_table_pays():
    sql = """ 
    CREATE TABLE IF NOT EXISTS pays (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id_telegram) ON DELETE CASCADE,
    amount FLOAT NOT NULL,
    date VARCHAR(255) NOT NULL,
    name_service VARCHAR(255) NOT NULL,
    comment VARCHAR(255) NOT NULL,
    status VARCHAR(255) NOT NULL,
    department_id INTEGER REFERENCES departments(id) ON DELETE CASCADE)
    """
    await db.pool.execute(sql)


async def create_table_spreadsheet_id():
    sql = """
    CREATE TABLE IF NOT EXISTS spread(
    id SERIAL PRIMARY KEY,
    spreadsheet_id VARCHAR(255) NOT NULL)
    """
    await db.pool.execute(sql)


async def create_table_spread_id():
    sql = """
    CREATE TABLE IF NOT EXISTS spread_project(
    id SERIAL PRIMARY KEY,
    sheet_id INTEGER NOT NULL, 
    sheet_title VARCHAR(255) NOT NULL,
    page INTEGER NOT NULL,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE)
    """
    await db.pool.execute(sql)
