from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from utils.db_api.department_controllers import get_departments, set_dep_status
from utils.db_api.project_controllers import set_admin_in_project, get_free_projects, get_pinned_projects, \
    select_in_project
from utils.db_api.users_controller import select_user, select_all_users, add_user, delete_user
from utils.db_api.utils import is_super_admin, get_users_for_admin
from utils.google_sheet.spreed_methods import update_spread

from aiogram.types import CallbackQuery
from loader import dp, bot


from keyboards.inline.workers_keyboard import user_menu, users_menu, permissions_menu
from keyboards.inline.project_keyboard import free_projects_kb, pinned_projects_menu, edit_project_menu
from keyboards.inline.departments_keyboard import pinned_departments_menu
from utils.callback import anchor_callback, user_call, pinned_project_call, delete_project, edit_project
from states.users_state import Users
from asyncpg.exceptions import UniqueViolationError
from aiogram.utils.exceptions import ChatNotFound


async def show_user(call, id):
    print(id)
    user = await select_user(id)
    user = user[0]
    msg = f'<b>ID USER</b> <code>{user["id_telegram"]}</code>\n' \
          f'<b>NICKNAME</b> <code>{user["nickname"]}</code>\n' \
          f'<b>ROLE</b> <code>{user["permissions"]}</code>'
    await call.message.edit_text(msg)
    await call.message.edit_reply_markup(user_menu(user["permissions"]))


@dp.callback_query_handler(text_contains='users')
async def users_menu_method(call: CallbackQuery):
    users = ''
    if is_super_admin(call.message.chat.id):
        users = await select_all_users()
    else:
        users = await get_users_for_admin(call.message.chat.id)
    await call.message.edit_text(f'Список юзеров ')
    await call.message.edit_reply_markup(users_menu(users))


@dp.callback_query_handler(text_contains='add_user')
async def add_user_method(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text('Введите имя пользователя')
    await Users.enter_name.set()


@dp.callback_query_handler(anchor_callback.filter(), state='*')
async def add_anchor(call: CallbackQuery, callback_data: dict, state: FSMContext):
    print('+')
    data = await state.get_data()
    user_id = callback_data.get('id_user')
    project_id = callback_data.get('id_project')
    await set_admin_in_project(user_id, project_id)
    free_frojects = await get_free_projects()
    await call.message.edit_reply_markup(free_projects_kb(free_frojects, data['id_telegram']))


@dp.message_handler(state=Users.enter_name)
async def enter_name_method(m: Message, state: FSMContext):
    await state.update_data(nickname=m.text)
    await m.answer('Введите id пользователя')
    await Users.enter_id.set()


@dp.message_handler(state=Users.enter_id)
async def enter_id_method(m: Message, state: FSMContext):
    await state.update_data(id_telegram=m.text)
    await m.answer('Выберите тип пользователя', reply_markup=permissions_menu())
    await Users.enter_permissions.set()


@dp.callback_query_handler(state='*', text_contains='create')
async def enter_projects(call: CallbackQuery, state: FSMContext):
    type_user = call.data.split('_')[1]
    data = await state.get_data()
    print(data)
    if type_user == 'admin':
        free_frojects = await get_free_projects()
        if len(free_frojects) > 0:
            await call.message.edit_text("Выберите один или несколько проектов")
            await call.message.edit_reply_markup(free_projects_kb(free_frojects, data['id_telegram']))
        else:
            await call.message.edit_text('Нет свободных проектов')
            users = await get_users_for_admin(call.message.chat.id)
            await call.message.edit_reply_markup(users_menu(users))
    else:
        await add_user(int(data['id_telegram']), data['nickname'], type_user)
        await call.message.edit_text('Пользователь добавлен')
        if is_super_admin(call.message.chat.id):
            users = await select_all_users()
        else:
            users = await get_users_for_admin(call.message.chat.id)
        await call.message.edit_reply_markup(users_menu(users))
        await update_spread()
        await state.finish()


@dp.callback_query_handler(state='*', text_contains='finish_anchor')
async def finish_add_user(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await add_user(int(data['id_telegram']), data['nickname'], 'admin')
    await call.message.edit_text('Пользователь добавлен')
    if is_super_admin(call.message.chat.id):
        users = await select_all_users()
    else:
        users = await get_users_for_admin(call.message.chat.id)
    await call.message.edit_reply_markup(users_menu(users))
    await update_spread()
    await state.finish()


"""
@dp.callback_query_handler(state=Users_state.enter_permissions, text_contains='create')
async def enter_permissions_metod(call: CallbackQuery, state: FSMContext):
    permissions = call.data.split('_')[1]
    data = await state.get_data()
    await utils.add_user(int(data['id_telegram']), data['nickname'], permissions)
    status_text = 'Список юзеров'
    if utils.is_super_admin(call.message.chat.id):
        users = await utils.select_all_users()
    else:
        users = await utils.get_users_for_admin(call.message.chat.id)
    await call.message.edit_text(status_text)
    await call.message.edit_reply_markup(users_menu(users))
    await update_spread()
    await state.finish()
"""


@dp.callback_query_handler(user_call.filter())
async def select_user_method(call: CallbackQuery, callback_data: dict, state: FSMContext):
    print('+++')
    id_user = callback_data.get('id')
    await show_user(call, id_user)
    await state.update_data(id=id_user)


@dp.callback_query_handler(text_contains='user_delete')
async def delete_user_method(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await delete_user(data['id'])
    await state.finish()
    users = ''
    if is_super_admin(call.message.chat.id):
        users = await select_all_users()
    else:
        users = await get_users_for_admin(call.message.chat.id)
    await call.message.edit_text('Список юзеров ')
    await call.message.edit_reply_markup(users_menu(users))


@dp.callback_query_handler(text_contains='pinnedProjects')
async def show_pinned_projects(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    print(data)
    projects = await get_pinned_projects(data['id'])
    print(projects)
    if len(projects) != 0:
        await call.message.edit_text('Закрепленные проекты')
        await call.message.edit_reply_markup(pinned_projects_menu(projects))
    else:
        await call.answer('У пользователя отсутствуют закрепление проекты')


@dp.callback_query_handler(pinned_project_call.filter())
async def edit_pinned_projects(call: CallbackQuery, callback_data: dict):
    id = callback_data.get('id')
    name = callback_data.get('name')
    await call.message.edit_text(name)
    await call.message.edit_reply_markup(edit_project_menu(id, name))


@dp.callback_query_handler(text_contains='backUser')
async def back_pinned_projects_method(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg = await show_user(call, data['id'])


@dp.callback_query_handler(delete_project.filter())
async def delete_method_p(call: CallbackQuery, callback_data: dict, state: FSMContext):
    id = callback_data.get('id')
    await delete_project(id)
    data = await state.get_data()
    await show_user(call, data['id'])


async def check_departments(call, name, project_id):
    departments = await select_in_project(project_id)
    departments_list = await get_departments(project_id)
    if len(departments_list) > 0:
        flag = departments_list[0]['status']
        await call.message.edit_text(name)
        await call.message.edit_reply_markup(pinned_departments_menu(departments, flag))
    else:
        await call.answer("В проекте нету отделов")


@dp.callback_query_handler(edit_project.filter())
async def pinned_departments(call: CallbackQuery, state: FSMContext, callback_data: dict):
    id = callback_data.get('id')
    name = callback_data.get('name')
    await state.update_data(project_id=id, project_name=name)
    await check_departments(call, name, int(id))


@dp.callback_query_handler(text_contains='closeAllDepartments')
async def close_all_departments(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await set_dep_status(data['project_id'], 'close')
    await check_departments(call, data['project_name'], int(data['project_id']))


@dp.callback_query_handler(text_contains='openAllDepartments')
async def open_all_departments(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await set_dep_status(data['project_id'], 'open')
    await check_departments(call, data['project_name'], int(data['project_id']))


@dp.callback_query_handler(text_contains='backPinnedProjects')
async def back_pinned_projects(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.edit_text(data['project_name'])
    await call.message.edit_reply_markup(edit_project_menu(data['project_id'], data['project_name']))
