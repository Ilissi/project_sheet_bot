from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup

from utils.callback import *
from utils.db_api.users_controller import is_admin
from utils.db_api.utils import is_super_admin


async def start_menu(url, id_user):
    k = InlineKeyboardMarkup()
    k.add(InlineKeyboardButton('Проекты', callback_data='projects'))
    print(is_super_admin(id_user))
    if is_super_admin(id_user):
        if url != 'N':
            k.add(InlineKeyboardButton('Google Sheets', url=url))
    if is_super_admin(id_user) or await is_admin(id_user):
        k.add(InlineKeyboardButton('Пользователи', callback_data='users'))
    return k


def select_admins_menu(admins):
    k = InlineKeyboardMarkup()
    for admin in admins:
        k.add(InlineKeyboardButton(admin['nickname'], callback_data='selectAdmin_' + str(admin['id'])))
    return k


def send_request(id_user, amount, date, name_service, comment):
    k = InlineKeyboardMarkup()
    print(id_user, amount, date, name_service, comment)
    k.add(InlineKeyboardButton('Принять', callback_data=accept_request_pay.new(
        i=id_user, a=amount, d=date, n=name_service, c=comment
    )))
    k.add(InlineKeyboardButton('Oтклонить',
                               callback_data=not_approved_pay.new(id_user=id_user, date=date, comment=comment)))
    return k