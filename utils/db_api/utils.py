from data.config import ADMINS
from utils.db_api.department_controllers import get_department_to_id, get_departments
from utils.db_api.order_controller import select_all_orders
from utils.db_api.project_controllers import get_project, get_pinned_projects
from utils.db_api.users_controller import get_user, get_worker, select_workers_in_department, get_username


async def is_unemployed_users(id):
    id_workers = await select_all_orders()
    for id_worker in id_workers:
        if id == id_worker['user_id']:
            return False
    return True


def is_super_admin(telegram_id):
    for admin in ADMINS:
        if admin == telegram_id:
            return True


def unique(list1):
    unique_list = []
    for x in list1:
        if x not in unique_list:
            unique_list.append(x)
    return unique_list


async def get_project_for_user(id):
    db_id = await get_user(id)
    orders = await get_worker(id)
    print(id, db_id[0]['id'], orders)
    projects_user = []
    for order in orders:
        projs = await get_department_to_id(order['department_id'])
        for proj in projs:
            projects_user.append(proj['project_id'])
    unique_projects = unique(projects_user)
    projects = []
    for id_project in unique_projects:
        p = await get_project(int(id_project))
        projects.append(p[0])
    return projects


async def get_departments_for_user(id):
    db_id = await get_user(id)
    orders = await get_worker(db_id[0]['id'])
    deps_user = []
    for order in orders:
        d = await get_department_to_id(order['department_id'])
        deps_user.append(d[0])
    return deps_user


async def get_users_for_admin(id):
    db_id = await get_user(id)
    projects = await get_pinned_projects(db_id[0]['id'])
    deps = []
    for project in projects:
        list_deps = await get_departments(project['id'])
        for dep in list_deps:
            deps.append(dep)
    id_users = []
    for dep in deps:
        user = await select_workers_in_department(dep['id'])
        if len(user) != 0:
            id_users.append(user[0]['user_id'])
    users = []
    for id_user in id_users:
        user = await get_username(id_user)
        users.append(user[0])
    return users
