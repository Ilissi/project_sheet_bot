from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import ChatNotFound

from data import config
from utils.db_api.order_controller import add_order, get_pays_for_worker
from utils.db_api.project_controllers import select_in_project, get_project
from utils.db_api.users_controller import select_workers_in_department, select_all_users, get_archive_users, \
    get_user_nickname, get_worker, set_status_worker, get_id_telegram
from utils.google_sheet.spreed_methods import create_spread
from aiogram.types import CallbackQuery
from loader import dp
from loader import bot
from states.add_pay import Pay
from states.search_pay import Search
from utils import date_pattern
from utils.callback import department_call, add_worker_call, add_user_to_department, add_pay, worker_call, archive, history_pays, unzip
from datetime import datetime
from keyboards.inline.departments_keyboard import departments_menu, back_users_in_dep
from keyboards.inline.workers_keyboard import workers_menu, select_unemployed_users_menu, worker_menu
from keyboards.inline.main_keyboard import start_menu, send_request



@dp.callback_query_handler(department_call.filter())
async def department_method(call: CallbackQuery, callback_data: dict, state: FSMContext):
    department_id = callback_data.get('id')
    department_name = callback_data.get('name')
    await state.update_data(department_id=department_id, department_name=department_name)
    workers = await select_workers_in_department(department_id)
    await call.message.edit_text(f'Работники отдела ' + department_name)
    await call.message.edit_reply_markup(await workers_menu(workers, department_id, call.message.chat.id))


@dp.callback_query_handler(text_contains='back_departments')
async def back_departmens(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    departments = await select_in_project(int(data['project_id']))
    await call.message.edit_text('Проект ' + data['project_name'])
    await state.update_data(department_id='x', department_name='x')
    await call.message.edit_reply_markup(await departments_menu(departments, call.message.chat.id))


@dp.callback_query_handler(add_worker_call.filter())
async def list_add_worker_menu(call: CallbackQuery):
    users = await select_all_users()
    count_unemployed_users = await select_unemployed_users_menu(users)
    if len(count_unemployed_users['inline_keyboard']) > 0:
        await call.message.edit_text('Выберите пользователя')
        await call.message.edit_reply_markup(await select_unemployed_users_menu(users))
    else:
        await call.answer('Нет свободных работников')


@dp.callback_query_handler(add_user_to_department.filter())
async def add_user_to_department_method(call: CallbackQuery, state: FSMContext, callback_data: dict):
    id_user = callback_data.get('id')
    data = await state.get_data()
    print(data['department_id'])
    await add_order(int(id_user), int(data['department_id']))
    workers = await select_workers_in_department(data['department_id'])
    await call.message.edit_text(f'Работники отдела ' + data['department_name'])
    await call.message.edit_reply_markup(await workers_menu(workers, data['department_id'], call.message.chat.id))


@dp.callback_query_handler(text_contains='employee_archive')
async def list_archive_users(call: CallbackQuery):
    users = await get_archive_users()
    msg = ''
    if len(users) != 0:
        for user in users:
            nickname = await get_user_nickname(str(user['user_id']))
            msg += f"<b>{nickname[0]['nickname']}</b> - <code>{user['user_id']}</code>\n"
        await call.message.edit_text(msg)
        await call.message.edit_reply_markup(back_users_in_dep())
    else:
        await call.answer('Нет архивированных работников')


@dp.callback_query_handler(text_contains='back_in_dep')
async def back_users_in_dep_method(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    workers = await select_workers_in_department(data['department_id'])
    await call.message.edit_text(f'Работники отдела ' + data['department_name'])
    await call.message.edit_reply_markup(await workers_menu(workers, data['department_id'], call.message.chat.id))


@dp.callback_query_handler(worker_call.filter())
async def worker_menu_method(call: CallbackQuery, callback_data: dict):
    id_user = callback_data.get('id')
    name = callback_data.get('name')
    await call.message.edit_text(name + ' выбран')
    status = await get_worker(id_user)
    status = status[0]['status']
    await call.message.edit_reply_markup(await worker_menu(status, id_user, name, call.message.chat.id))


@dp.callback_query_handler(text_contains='backWorkerInDep')
async def back_worker_in_dep(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    workers = await select_workers_in_department(data['department_id'])
    await call.message.edit_text(f'Работники отдела ' + data['department_name'])
    await call.message.edit_reply_markup(await workers_menu(workers, data['department_id'], call.message.chat.id))


async def show_worker(call, id, name):
    await call.message.edit_text(name + ' выбран')
    status = await get_worker(id)
    status = status[0]['status']
    await call.message.edit_reply_markup(await worker_menu(status, id, name, call.message.chat.id))


@dp.callback_query_handler(archive.filter())
async def archive_method(call: CallbackQuery, state: FSMContext, callback_data: dict):
    id = callback_data.get('id')
    await state.update_data(user_id=id)
    name = callback_data.get('name')
    await set_status_worker(id, 'archive')
    await show_worker(call, id, name)


@dp.callback_query_handler(unzip.filter())
async def unzip_method(call: CallbackQuery, callback_data: dict):
    id = callback_data.get('id')
    name = callback_data.get('name')
    await set_status_worker(id, 'worked')
    await show_worker(call, id, name)


@dp.callback_query_handler(add_pay.filter())
async def add_pay_method(call: CallbackQuery, state: FSMContext, callback_data: dict):
    await call.message.edit_text('Введите сумму')
    await Pay.enter_ammount.set()


@dp.message_handler(state=Pay.enter_amount)
async def enter_pay_method(m: Message, state: FSMContext):
    try:
        num = float(m.text)
        await state.update_data(amount=m.text)
        await m.answer('Введите название услуги')
        await Pay.enter_name_service.set()
    except Exception as e:
        await m.answer('Неверно указана сумма')


@dp.message_handler(state=Pay.enter_name_service)
async def enter_name_service(m: Message, state: FSMContext):
    await state.update_data(name_service=m.text)
    await m.answer('Введите дату в формате ДД-ММ-ГГГГ ')
    await Pay.enter_date.set()


@dp.message_handler(state=Pay.enter_date)
async def enter_date(m: Message, state: FSMContext):
    try:
        list_date = m.text.split('-')
        if len(list_date) == 3:
            day = int(list_date[0])
            mon = int(list_date[1])
            year = int(list_date[2])
            date = datetime(year, mon, day)
            await state.update_data(date=m.text)
            await m.answer('Введите комментарий')
            await Pay.enter_comment.set()
        else:
            await m.answer('Не верно указана дата\nДД-ММ-ГГГГ')
    except:
        await m.answer('Не верно указана дата\nДД-ММ-ГГГГ')


@dp.message_handler(state=Pay.enter_comment)
async def enter_comment(m: Message, state: FSMContext):
    data = await state.get_data()
    project = await get_project(data['project_id'])
    user = await get_id_telegram(str(project[0]['admin']))
    id_user = int(user[0]['id_telegram'])
    amount = data['amount']
    department_id = data['department_id']
    msg = f"Отправлен запрос на оплату\nСумма <code>{data['amount']}</code> \n" \
          f"Дата <code>{data['date']}</code>\n" \
          f"Название услуги <code>{data['name_service']}</code>\n" \
          f"Комментарий <code>{m.text}</code>"
    try:
        await bot.send_message(id_user, msg,
                               reply_markup=send_request(str(m.chat.id), amount, data['date'], data['name_service'],
                                                         m.text + '*' + department_id))
        await m.answer(msg, reply_markup=await start_menu(config.url_sheet, m.chat.id))
    except ChatNotFound as e:
        print(str(e))
        await state.finish()
        await m.answer('Пользователь не найден', reply_markup=await start_menu(await create_spread(), m.chat.id))
    except ValueError as e:
        await state.finish()
        await m.answer('Очень длинный запрос, невозможно отправить\n' + str(e),
                       reply_markup=await start_menu(await create_spread(), m.chat.id))


@dp.callback_query_handler(history_pays.filter())
async def enter_search_date(call: CallbackQuery, state: FSMContext, callback_data: dict):
    search_user_id = callback_data.get('id')
    await call.message.edit_text('Введите промежуток дат в формате ДД-ММ-ГГГГ / ДД-ММ-ГГГГ')
    await state.update_data(search_user_id=search_user_id)
    await Search.enter_date.set()


@dp.message_handler(state=Search.enter_date)
async def search_pay(m: Message, state: FSMContext):
    delta = m.text
    data = await state.get_data()
    await state.finish()
    id_user = data['search_user_id']
    if date_pattern.check_date(delta):
        dates = date_pattern.get_delta(delta)
        user = await get_id_telegram(id_user)
        try:
            pays = await get_pays_for_worker(str(user[0]['id_telegram']))
            results = ''
            if len(pays) != 0:
                for pay in pays:
                    date = date_pattern.to_datetime(pay['date'])
                    print(dates[0], date)
                    if dates[0] <= date <= dates[1]:
                        results += f"🔶 ID user <code>{str(pay['user_id'])}</code>\n" \
                                   f"Cумма <code>{str(pay['amount'])}</code>\n" \
                                   f"Дата <code>{str(pay['date'])}</code>\n" \
                                   f"Описание услуги <code>{pay['name_service']}</code>"
            if len(results) > 0:
                await m.answer(results)
            else:
                await m.answer('Оплаты не найдены', reply_markup=await start_menu(await create_spread(), m.chat.id))
        except:
            await m.answer('Оплаты не найдены', reply_markup=await start_menu(await create_spread(), m.chat.id))
    else:
        await m.answer('Неверный промежуток попробуйте еще раз\nДД-ММ-ГГГГ / ДД-ММ-ГГГГ')
