from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup


from utils.callback import department_call
from utils.db_api.users_controller import is_admin
from utils.db_api.utils import is_super_admin


async def departments_menu(departments, id_user):
    k = InlineKeyboardMarkup()
    for department in departments:
        k.add(InlineKeyboardButton(department['name'], callback_data=department_call.new(id=str(department['id']),
                                                                                         name=department['name'])))
    if await is_admin(id_user) or is_super_admin(id_user):
        k.add(InlineKeyboardButton('Создать отдел', callback_data='add_department'))
    if is_super_admin(id_user):
        k.add(InlineKeyboardButton('Удалить проект', callback_data='delete_project'))
    k.add(InlineKeyboardButton('Назад', callback_data='back_projects'))
    return k


def pinned_departments_menu(departments, flag):
    k = InlineKeyboardMarkup()
    for department in departments:
        k.add(InlineKeyboardButton(department['name'], callback_data='x'))
    if flag == "open":
        k.add(InlineKeyboardButton('Закрыть все отделы', callback_data='closeAllDepartments'))
    else:
        k.add(InlineKeyboardButton('Открыть все отделы', callback_data='openAllDepartments'))
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