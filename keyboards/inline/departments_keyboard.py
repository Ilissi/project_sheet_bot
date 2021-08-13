from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup

from utils.callback import department_call, add_admin_to_department, adds_user_to_department, edit_department, \
    set_status_department, edit_project, remove_admin_from_department
from utils.db_api.order_controller import get_department_by_user_id, get_dep_admin
from utils.db_api.users_controller import is_admin
from utils.db_api.utils import is_super_admin


async def departments_menu(departments, id_user):
    k = InlineKeyboardMarkup()
    for department in departments:
        k.add(InlineKeyboardButton(department['department_name'],
                                   callback_data=department_call.new(id=str(department['id']),
                                                                     name=department['department_name'])))
    if await is_admin(id_user) or is_super_admin(id_user):
        k.add(InlineKeyboardButton('Создать отдел', callback_data='add_department'))
    if is_super_admin(id_user):
        k.add(InlineKeyboardButton('Удалить проект', callback_data='delete_project'))
    k.add(InlineKeyboardButton('Назад', callback_data='back_projects'))
    return k


def pinned_departments_menu(departments):
    k = InlineKeyboardMarkup()
    for department in departments:
        k.add(InlineKeyboardButton(department['department_name'],
                                   callback_data=edit_department.new(id_department=department['id'])))
    k.add(InlineKeyboardButton('Назад', callback_data='backPinnedProjects'))
    return k


def back_users_in_dep():
    k = InlineKeyboardMarkup()
    k.add(InlineKeyboardButton('Назад', callback_data='back_in_dep'))
    return k


def confirm_delete_department():
    k = InlineKeyboardMarkup()
    k.add(InlineKeyboardButton('ДА', callback_data='departmentConfirmDelete'),
          InlineKeyboardButton('НЕТ', callback_data='back_departments'))
    return k


async def add_admin_to_department_keyboard(departments, user_id, project_id):
    admin_to_department_keyboard = InlineKeyboardMarkup()
    for department in departments:
        get_order = await get_dep_admin(int(department['id']), int(user_id))
        if len(get_order) == 0:
            admin_to_department_keyboard.add(InlineKeyboardButton(department['department_name'], callback_data='x'),
                                             InlineKeyboardButton('Закрепить', callback_data=add_admin_to_department.new(
                                                id_department=department['id'], id_user=user_id, id_project=project_id)))
        elif len(get_order) >= 1:
            admin_to_department_keyboard.add(InlineKeyboardButton(department['department_name'], callback_data='x'),
                                             InlineKeyboardButton('Открепить', callback_data=remove_admin_from_department.new(
                                                 id_department=department['id'], id_user=user_id, id_project=project_id)))
    admin_to_department_keyboard.add(InlineKeyboardButton('Назад', callback_data='users_back'))
    return admin_to_department_keyboard


async def add_user_to_department_keyboard(departments, user_id, project_id):
    user_to_department_keyboard = InlineKeyboardMarkup()
    for department in departments:
        orders = await get_department_by_user_id(int(department['id']), int(user_id))
        if len(orders) == 0:
            user_to_department_keyboard.add(InlineKeyboardButton(department['department_name'], callback_data='x'),
                                            InlineKeyboardButton('Закрепить', callback_data=adds_user_to_department.new(
                                                id_department=department['id'], id_user=user_id, id_project=project_id)))
    user_to_department_keyboard.add(InlineKeyboardButton('Назад', callback_data='users_back'))
    return user_to_department_keyboard


async def close_open_department(department, project_id, project_name):
    close_open_department_keyboard = InlineKeyboardMarkup()
    if department['status'] == 'open':
        close_open_department_keyboard.add(InlineKeyboardButton('⛔️ Закрыть отдел',
                                           callback_data=set_status_department.new(
                                                id_department=department['id'], status='close')))
    elif department['status'] == 'close':
        close_open_department_keyboard.add(InlineKeyboardButton('✅ Открыть отдел',
                                           callback_data=set_status_department.new(
                                                id_department=department['id'], status='open')))
    close_open_department_keyboard.add(InlineKeyboardButton('Назад', callback_data=edit_project.new(
                                       id=project_id, name=project_name)))
    return close_open_department_keyboard

