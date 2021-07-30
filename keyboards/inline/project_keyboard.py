from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup


from utils.callback import project_call, pinned_project_call, anchor_callback, edit_project, delete_project
from utils.db_api.utils import is_super_admin


def projects_menu(projects, id_user):
    k = InlineKeyboardMarkup()
    for project in projects:
        k.add(InlineKeyboardButton(project['name'], callback_data=project_call.new(id=str(project['id']),
                                                                                   name=project['name'])))
    if is_super_admin(id_user):
        k.add(InlineKeyboardButton('Добавить проект', callback_data='add_project'))
    k.add(InlineKeyboardButton('Назад', callback_data='back_main_menu'))
    return k


def pinned_projects_menu(projects):
    k = InlineKeyboardMarkup()
    for project in projects:
        k.add(InlineKeyboardButton(project['name'], callback_data=pinned_project_call.new(name=project['name'],
                                                                                          id=project['id'])))
    return k


def confirm_delete():
    k = InlineKeyboardMarkup()
    k.add(InlineKeyboardButton('ДА', callback_data='confirmDelete'),
          InlineKeyboardButton('НЕТ', callback_data='proj_back'))
    return k


def edit_project_menu(id, name):
    k = InlineKeyboardMarkup()
    k.add(InlineKeyboardButton('Настроить проект', callback_data=edit_project.new(id=id, name=name)))
    k.add(InlineKeyboardButton('Удалить проект', callback_data=delete_project.new(id)))
    k.add(InlineKeyboardButton('Назад', callback_data='backUser'))
    return k


def free_projects_kb(projects, id):
    k = InlineKeyboardMarkup()
    if len(projects) != 0:
        for project in projects:
            k.add(InlineKeyboardButton(project['name'], callback_data='x'),
                  InlineKeyboardButton('Закрепить', callback_data=anchor_callback.new(str(project['id']), str(id))))
        k.add(InlineKeyboardButton('Далее', callback_data='finish_anchor'))
    else:
        k.add(InlineKeyboardButton('Далее', callback_data='finish_anchor'))
    return k