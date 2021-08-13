from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup

from utils.callback import *
from utils.db_api.utils import is_super_admin


async def start_menu(url, id_user):
    k = InlineKeyboardMarkup()
    k.add(InlineKeyboardButton('Проекты', callback_data='projects'))
    if is_super_admin(id_user):
        if url != 'N':
            k.add(InlineKeyboardButton('Google Sheets', url=url))
    if is_super_admin(id_user):
        k.add(InlineKeyboardButton('Пользователи', callback_data='users'))
    return k


def select_admins_menu(admins):
    k = InlineKeyboardMarkup()
    for admin in admins:
        k.add(InlineKeyboardButton(admin['nickname'], callback_data='selectAdmin_' + str(admin['id'])))
    return k


def send_request(pay_id):
    k = InlineKeyboardMarkup()
    k.add(InlineKeyboardButton('Принять', callback_data=accept_request_pay.new(pay_id=pay_id)))
    k.add(InlineKeyboardButton('Oтклонить', callback_data=not_approved_pay.new(pay_id=pay_id)))
    return k


def send_request_main_admin(pay_id):
    k = InlineKeyboardMarkup()
    k.add(InlineKeyboardButton('Принять', callback_data=accept_request_pay_admin.new(pay_id=pay_id)))
    k.add(InlineKeyboardButton('Отклонить', callback_data=not_approved_pay_admin.new(pay_id=pay_id)))
    return k