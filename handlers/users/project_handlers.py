from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from asyncpg.exceptions import UniqueViolationError

from utils.db_api.project_controllers import select_all_projects, add_project,  delete_project
from utils.db_api.users_controller import is_admin, is_user
from utils.db_api.utils import get_project_for_user, is_super_admin
from utils.google_sheet.spreed_methods import update_spread

from aiogram.types import CallbackQuery
from loader import dp


from keyboards.inline.project_keyboard import projects_menu, confirm_delete
from states.project_state import Projects


@dp.callback_query_handler(text_contains='back_projects')
@dp.callback_query_handler(text_contains='projects')
async def projects_method(call: CallbackQuery, state: FSMContext):
    await state.finish()
    projects = ''
    if await is_user(call.message.chat.id) or await is_admin(call.message.chat.id):
        projects = await get_project_for_user(call.message.chat.id)
    elif is_super_admin(call.message.chat.id):
        projects = await select_all_projects()
    await call.message.edit_text('Меню проектов')
    await call.message.edit_reply_markup(projects_menu(projects, call.message.chat.id))


@dp.callback_query_handler(text_contains='delete_project')
async def delete_project_method(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.edit_text(f'Вы хотите удалить {data["project_name"]} ?')
    await call.message.edit_reply_markup(confirm_delete())


@dp.callback_query_handler(text_contains='confirmDelete')
async def confirm_delete_project(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.finish()
    await delete_project(data['project_id'])
    projects = await select_all_projects()
    await call.message.edit_text(data['project_name'] + ' удален')
    await call.message.edit_reply_markup(projects_menu(projects, call.message.chat.id))
    await update_spread()


@dp.callback_query_handler(text_contains='add_project')
async def add_project_method(call: CallbackQuery):
    await call.message.edit_text('Введите название проекта')
    await Projects.enter_name.set()


@dp.message_handler(state=Projects.enter_name)
async def enter_admin(m: Message, state: FSMContext):
    await state.update_data(name_project=m.text)
    data = await state.get_data()
    try:
        await add_project(data['name_project'])
        await state.finish()
        projects = await select_all_projects()
        await m.answer('Меню проектов', reply_markup=projects_menu(projects, m.chat.id))
        await update_spread()
    except UniqueViolationError as e:
        await state.finish()
        projects = await select_all_projects()
        await m.answer('Меню проектов', reply_markup=projects_menu(projects, m.chat.id))


@dp.callback_query_handler(text_contains='selectAdmin', state=Projects.enter_admin)
async def create_project_method(call: CallbackQuery, state: FSMContext):
    admin_id = call.data.split('_')[1]
    data = await state.get_data()
    try:
        await add_project(data['name_project'], int(admin_id))
        await state.finish()
        projects = await select_all_projects()
        await call.message.edit_text('Меню проектов')
        await call.message.edit_reply_markup(reply_markup=projects_menu(projects, call.message.chat.id))
        await update_spread()
    except UniqueViolationError as e:
        await state.finish()
        projects = await select_all_projects()
        await call.message.edit_text('Меню проектов')
        await call.message.edit_reply_markup(reply_markup=projects_menu(projects, call.message.chat.id))
