from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from utils.db_api.department_controllers import set_dep_status, get_departments_for_add_admin, \
    get_departments_for_add_user,  get_department_to_id
from utils.db_api.order_controller import add_order, set_dep_admin,  delete_dep_admin
from utils.db_api.project_controllers import select_all_projects, clear_admin_project
from utils.db_api.users_controller import select_user, select_all_users, add_user, delete_user
from utils.db_api.utils import is_super_admin, get_users_for_admin
from utils.google_sheet.spreed_methods import update_spread

from aiogram.types import CallbackQuery
from loader import dp, bot


from keyboards.inline.workers_keyboard import user_menu, users_menu, permissions_menu, back_user_menu
from keyboards.inline.project_keyboard import pinned_projects_menu, edit_project_menu, select_project_for_add
from keyboards.inline.departments_keyboard import pinned_departments_menu, add_admin_to_department_keyboard, \
    add_user_to_department_keyboard, close_open_department
from utils.callback import anchor_callback, user_call, pinned_project_call, delete_project, edit_project, \
    add_admin_to_department, adds_user_to_department, edit_department, set_status_department, \
    remove_admin_from_department
from states.users_state import Users
from asyncpg.exceptions import UniqueViolationError
from aiogram.utils.exceptions import ChatNotFound


async def show_user(call, id):
    user = await select_user(id)
    user = user[0]
    msg = f'<b>ID USER</b> <code>{user["id_telegram"]}</code>\n' \
          f'<b>NICKNAME</b> <code>{user["nickname"]}</code>\n' \
          f'<b>ROLE</b> <code>{user["permissions"]}</code>'
    await call.message.edit_text(msg)
    await call.message.edit_reply_markup(user_menu(user["permissions"]))


@dp.callback_query_handler(text_contains='users')
async def users_menu_method(call: CallbackQuery):
    if is_super_admin(call.message.chat.id):
        users = await select_all_users()
    else:
        users = await get_users_for_admin(call.message.chat.id)
    await call.message.edit_text(f'Список пользователей ')
    await call.message.edit_reply_markup(users_menu(users))


@dp.callback_query_handler(text_contains='add_user')
async def add_user_method(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text('Введите имя пользователя')
    await Users.enter_name.set()


@dp.callback_query_handler(anchor_callback.filter(), state='*')
async def add_anchor(call: CallbackQuery, callback_data: dict, state: FSMContext):
    user_id = callback_data.get('id_user')
    project_id = callback_data.get('id_project')
    user = await select_user(user_id)
    if user[0]['permissions'] == 'admin':
        departments = await get_departments_for_add_admin(int(project_id))
        await call.message.edit_text('Измени руководителя отдела')
        await call.message.edit_reply_markup(reply_markup=await add_admin_to_department_keyboard(departments, user_id, project_id))
    elif user[0]['permissions'] == 'user':
        departments = await get_departments_for_add_user(int(project_id))
        await call.message.edit_text('Закрепи пользователя за отделом')
        await call.message.edit_reply_markup(reply_markup=await add_user_to_department_keyboard(departments, user_id, project_id))


@dp.callback_query_handler(add_admin_to_department.filter())
async def admin_to_department(call: CallbackQuery, callback_data: dict, state: FSMContext):
    telegram_id = callback_data.get('id_user')
    department_id = callback_data.get('id_department')
    project_id = callback_data.get('id_project')
    set_admin = await set_dep_admin(int(department_id), int(telegram_id))
    departments = await get_departments_for_add_admin(int(project_id))
    await call.message.edit_text('Измени руководителя отдела')
    await call.message.edit_reply_markup(reply_markup=await add_admin_to_department_keyboard(departments, telegram_id, project_id))


@dp.callback_query_handler(remove_admin_from_department.filter())
async def admin_to_department(call: CallbackQuery, callback_data: dict, state: FSMContext):
    telegram_id = callback_data.get('id_user')
    department_id = callback_data.get('id_department')
    project_id = callback_data.get('id_project')
    set_admin = await delete_dep_admin(int(department_id), int(telegram_id))
    departments = await get_departments_for_add_admin(int(project_id))
    await call.message.edit_text('Измени руководителя отдела')
    await call.message.edit_reply_markup(reply_markup=await add_admin_to_department_keyboard(departments, telegram_id, project_id))


@dp.callback_query_handler(adds_user_to_department.filter())
async def user_to_department(call: CallbackQuery, callback_data: dict):
    telegram_id = callback_data.get('id_user')
    department_id = callback_data.get('id_department')
    project_id = callback_data.get('id_project')
    set_user = await add_order(int(telegram_id), int(department_id))
    departments = await get_departments_for_add_admin(int(project_id))
    await call.message.edit_text('Закрепи пользователя за отделом')
    await call.message.edit_reply_markup(reply_markup=await add_user_to_department_keyboard(departments, telegram_id, project_id))


@dp.message_handler(state=Users.enter_name)
async def enter_name_method(m: Message, state: FSMContext):
    await state.update_data(nickname=m.text)
    await m.answer('Введите id пользователя')
    await Users.enter_id.set()


@dp.message_handler(lambda message: not message.text.isdigit(), state=Users.enter_id)
async def get_amount(message: Message, state: FSMContext):
    await message.answer('Неправильно указана Telegram ID, попробуй еще раз!')


@dp.message_handler(lambda message: message.text.isdigit(), state=Users.enter_id)
async def enter_id_method(m: Message, state: FSMContext):
    await state.update_data(id_telegram=m.text)
    await m.answer('Выберите тип пользователя', reply_markup=permissions_menu())
    await Users.enter_permissions.set()


@dp.callback_query_handler(state='*', text_contains='create')
async def enter_projects(call: CallbackQuery, state: FSMContext):
    type_user = call.data.split('_')[1]
    data = await state.get_data()
    try:
        await add_user(int(data['id_telegram']), data['nickname'], type_user)
        await call.message.edit_text('Пользователь добавлен')
    except:
        await call.message.edit_text('Пользователь уже зарегистрирован в боте!')
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


@dp.callback_query_handler(user_call.filter())
async def select_user_method(call: CallbackQuery, callback_data: dict, state: FSMContext):
    id_user = callback_data.get('id')
    await show_user(call, id_user)
    await state.update_data(id=id_user)


@dp.callback_query_handler(text_contains='user_delete')
async def delete_user_method(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await delete_user(data['id'])
    await clear_admin_project(data['id'])
    await state.finish()
    if is_super_admin(call.message.chat.id):
        users = await select_all_users()
    else:
        users = await get_users_for_admin(call.message.chat.id)
    await call.message.edit_text('Список юзеров ')
    await call.message.edit_reply_markup(users_menu(users))


@dp.callback_query_handler(text_contains='pinnedProjects')
async def show_pinned_projects(call: CallbackQuery, state: FSMContext):
    projects = await select_all_projects()
    if len(projects) != 0:
        await call.message.edit_text('Выбери проект')
        await call.message.edit_reply_markup(pinned_projects_menu(projects))
    else:
        await call.answer('У пользователя отсутствуют закрепление проекты')


@dp.callback_query_handler(text_contains='pinNewProject')
async def add_pinned_departments(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    projects = await select_all_projects()
    if len(projects) == 0:
        await call.message.edit_text('Проектов нету')
        await call.message.edit_reply_markup(reply_markup=await back_user_menu())
    else:
        await call.message.edit_text('Выберите проект')
        await call.message.edit_reply_markup(reply_markup=await select_project_for_add(projects, data))



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
    departments_list_for_search = await get_departments_for_add_admin(project_id)
    if len(departments_list_for_search) > 0:
        await call.message.edit_text(name)
        await call.message.edit_reply_markup(pinned_departments_menu(departments_list_for_search))
    else:
        await call.answer("В руководителя нету закрепленных отделов")


@dp.callback_query_handler(edit_project.filter())
async def pinned_departments(call: CallbackQuery, state: FSMContext, callback_data: dict):
    id_user = await state.get_data()
    id = callback_data.get('id')
    name = callback_data.get('name')
    if 'project_id' not in id_user:
        await state.update_data(project_id=id, project_name=name, user_id=id_user['id'])
    await check_departments(call, name, int(id))


@dp.callback_query_handler(text_contains='backPinnedProjects')
async def back_pinned_projects(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.edit_text(data['project_name'])
    await call.message.edit_reply_markup(edit_project_menu(data['project_id'], data['project_name']))


@dp.callback_query_handler(edit_department.filter())
async def edit_department(call: CallbackQuery, state: FSMContext, callback_data: dict):
    department_id = callback_data.get('id_department')
    department = await get_department_to_id(int(department_id))
    data = await state.get_data()
    await call.message.edit_text(department[0]['department_name'])
    await call.message.edit_reply_markup(reply_markup=await close_open_department(department[0],
                                         data['project_id'], data['project_name']))


@dp.callback_query_handler(set_status_department.filter())
async def set_status_department(call: CallbackQuery, state: FSMContext, callback_data: dict):
    department_id = callback_data.get('id_department')
    department_status = callback_data.get('status')
    await set_dep_status(department_id, department_status)
    data = await state.get_data()
    await check_departments(call, data['project_name'], int(data['project_id']))
    await call.answer("Статус отдела изменен")


