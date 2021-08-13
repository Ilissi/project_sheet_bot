from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup


from utils.callback import worker_call, add_worker_call, user_call, add_user_to_department, unzip, archive, \
    history_pays, add_pay, department_call
from utils.db_api.users_controller import is_admin, get_user_nickname, is_user
from utils.db_api.utils import is_super_admin


async def workers_menu(workers, department_id, id_user):
    k = InlineKeyboardMarkup()
    if await is_user(id_user):
        for worker in workers:
            name_worker = await get_user_nickname(str(worker['user_id']))
            print(name_worker, worker['user_id'])
            if int(worker['user_id']) == id_user:
                k.add(InlineKeyboardButton(name_worker[0]['nickname'],
                                           callback_data=worker_call.new(id=str(worker['user_id']),
                                                                         name=name_worker[0][
                                                                             'nickname'])))
            else:
                k.add(InlineKeyboardButton(name_worker[0]['nickname'], callback_data='x'))
    else:
        for worker in workers:
            name_worker = await get_user_nickname(str(worker['user_id']))
            print(name_worker, worker['user_id'])
            k.add(InlineKeyboardButton(name_worker[0]['nickname'],
                                       callback_data=worker_call.new(id=str(worker['user_id']),
                                                                     name=name_worker[0][
                                                                         'nickname'])))
    if await is_admin(id_user) or is_super_admin(id_user):
        k.add(InlineKeyboardButton('Добавить работника', callback_data=add_worker_call.new(department_id)))
        k.add(InlineKeyboardButton('Архив работников', callback_data='employee_archive'))
    if is_super_admin(id_user):
        k.add(InlineKeyboardButton('Удалить отдел', callback_data='department_delete'))
    k.add(InlineKeyboardButton('Назад', callback_data='back_departments'))
    return k


def users_menu(users):
    k = InlineKeyboardMarkup()
    for user in users:
        k.add(InlineKeyboardButton(user['nickname'], callback_data=user_call.new(str(user['id_telegram']))))
    k.add(InlineKeyboardButton('Добавить пользователя', callback_data='add_user'))
    k.add(InlineKeyboardButton('Назад', callback_data='back_main_menu'))
    return k


def user_menu(role):
    k = InlineKeyboardMarkup()
    if role == 'admin':
        k.add(InlineKeyboardButton('Закрепленные отделы', callback_data='pinnedProjects'))
    k.add(InlineKeyboardButton('Закрепить пользователя', callback_data='pinNewProject'))
    k.add(InlineKeyboardButton('Удалить пользователя', callback_data='user_delete'))
    k.add(InlineKeyboardButton('Назад', callback_data='users_back'))
    return k


def permissions_menu():
    k = InlineKeyboardMarkup()
    k.add(InlineKeyboardButton('Руководитель', callback_data='create_admin'))
    k.add(InlineKeyboardButton('Работник', callback_data='create_user'))
    return k


async def select_unemployed_users_menu(users, data):
    k = InlineKeyboardMarkup()
    for user in users:
        print(user)
        k.add(InlineKeyboardButton(user['nickname'], callback_data=add_user_to_department.new(user['id_telegram'])))
    k.add(InlineKeyboardButton('Назад', callback_data=department_call.new(name=data['department_name'], id=data['department_id'])))
    return k


async def worker_menu(status, user_id, name, id_telegram):
    k = InlineKeyboardMarkup()
    if await is_admin(id_telegram) or is_super_admin(id_telegram):
        if status == 'archive':
            k.add(InlineKeyboardButton('Разархивировать работника', callback_data=unzip.new(id=user_id, name=name)))
        else:
            k.add(InlineKeyboardButton('Заархивировать работника', callback_data=archive.new(id=user_id, name=name)))
    k.add(InlineKeyboardButton('Посмотреть историю оплат', callback_data=history_pays.new(user_id)))
    k.add(InlineKeyboardButton('Добавить оплату', callback_data=add_pay.new(user_id)))
    k.add(InlineKeyboardButton('Назад', callback_data='backWorkerInDep'))
    return k


async def back_user_menu():
    back_user_menu_keyboard = InlineKeyboardMarkup()
    back_user_menu_keyboard.add(InlineKeyboardButton('Назад', callback_data='users_back'))
    return back_user_menu_keyboard


