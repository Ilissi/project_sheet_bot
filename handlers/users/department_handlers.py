from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from asyncpg.exceptions import UniqueViolationError
from aiogram.types import CallbackQuery

from utils.db_api.department_controllers import get_departments, add_department, delete_department
from utils.google_sheet.spreed_methods import update_spread
from loader import dp
from states.departments_state import Departments

from utils.callback import project_call
from keyboards.inline.departments_keyboard import departments_menu, confirm_delete_department


@dp.callback_query_handler(project_call.filter())
async def departments_method(call: CallbackQuery, callback_data: dict, state: FSMContext):
    project_id = callback_data.get('id')
    project_name = callback_data.get('name')
    departments = await get_departments(int(project_id))
    await call.message.edit_text(project_name + ' меню')
    await call.message.edit_reply_markup(await departments_menu(departments, call.message.chat.id))
    await state.update_data(project_id=project_id, project_name=project_name)


@dp.callback_query_handler(text_contains='proj_back')
async def back_project(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    departments = await get_departments(int(data['project_id']))
    await call.message.edit_text(data['project_name'])
    await call.message.edit_reply_markup(await departments_menu(departments, call.message.chat.id))


@dp.callback_query_handler(text_contains='department_delete')
async def delete_department_method(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.edit_text(f'Вы хотите удалить {data["department_name"]} ?')
    await call.message.edit_reply_markup(confirm_delete_department())


@dp.callback_query_handler(text_contains='departmentConfirmDelete')
async def confirm_delete_departments(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await delete_department(data['department_id'])
    departments = await get_departments(int(data['project_id']))
    await call.message.edit_text(data['department_name'] + ' удален')
    await state.update_data(department_id='x', department_name='x')
    await call.message.edit_reply_markup(await departments_menu(departments, call.message.chat.id))
    await update_spread()


@dp.callback_query_handler(text_contains='add_department')
async def add_department_method(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text('Введите название отдела')
    await Departments.enter_name.set()


@dp.message_handler(state=Departments.enter_name)
async def enter_name_department(m: Message, state: FSMContext):
    name = m.text
    data = await state.get_data()
    try:
        await add_department(int(data['project_id']), name)
        await state.finish()
        await state.update_data(project_id=data['project_id'], project_name=data['project_name'])
        departments = await get_departments(int(data['project_id']))
        await m.answer(data['project_name'] + ' меню ', reply_markup=await departments_menu(departments, m.chat.id))
        await update_spread()
    except UniqueViolationError:
        await state.finish()
        await state.update_data(project_id=data['project_id'], project_name=data['project_name'])
        departments = await get_departments(int(data['project_id']))
        await m.answer('Такой отдел уже существует', reply_markup=await departments_menu(departments, m.chat.id))
