from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import ChatNotFound

from states import Decline
from utils.db_api.order_controller import add_order, get_pays_for_worker, get_dep_admin, get_department_admin, \
    add_pay_for_user, update_status_pay, get_pay_by_id
from utils.db_api.project_controllers import select_in_project
from utils.db_api.users_controller import select_workers_in_department, get_archive_users, \
    get_user_nickname, get_worker, set_status_worker, get_id_telegram, select_all_users_for_add, get_user_role, \
    is_user, is_admin
from utils.db_api.utils import is_super_admin
from utils.google_sheet.spreed_methods import create_spread, update_spread
from aiogram.types import CallbackQuery
from loader import dp
from loader import bot
from states.add_pay import Pay
from states.search_pay import Search
from utils import date_pattern
from utils.callback import department_call, add_worker_call, add_user_to_department, add_pay, worker_call, archive, \
    history_pays, unzip, accept_request_pay_admin, not_approved_pay_admin, not_approved_pay, accept_request_pay
from datetime import datetime
from keyboards.inline.departments_keyboard import departments_menu, back_users_in_dep
from keyboards.inline.workers_keyboard import workers_menu, select_unemployed_users_menu, worker_menu
from keyboards.inline.main_keyboard import start_menu, send_request, send_request_main_admin
from data.config import ADMINS


@dp.callback_query_handler(department_call.filter())
async def department_method(call: CallbackQuery, callback_data: dict, state: FSMContext):
    department_id = callback_data.get('id')
    department_name = callback_data.get('name')
    user_id = call.message.chat.id
    user_role = await get_user_role(int(department_id), int(user_id))
    if is_super_admin(user_id) or user_role[0]['status'] == 'admin':
        await state.update_data(department_id=department_id, department_name=department_name)
        workers = await select_workers_in_department(department_id)
        await call.message.edit_text(f'Работники отдела ' + department_name)
        await call.message.edit_reply_markup(await workers_menu(workers, department_id, user_id))
    elif user_role[0]['status'] == 'worked':
        await state.update_data(department_id=department_id, department_name=department_name)
        await call.message.edit_text(f'Вы работник - ' + department_name)
        await call.message.edit_reply_markup(await workers_menu(user_role, department_id, user_id))
    elif user_role[0]['status'] == 'archive':
        await call.answer('Администратор добавил Вас в архив')


@dp.callback_query_handler(text_contains='back_departments')
async def back_departments(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    departments = await select_in_project(int(data['project_id']))
    await call.message.edit_text('Проект ' + data['project_name'])
    await state.update_data(department_id='x', department_name='x')
    await call.message.edit_reply_markup(await departments_menu(departments, call.message.chat.id))


@dp.callback_query_handler(add_worker_call.filter())
async def list_add_worker_menu(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    users = await select_all_users_for_add()
    user_list = []
    for user in users:
        check_user = await get_dep_admin(int(data['department_id']), int(user['id_telegram']))
        if len(check_user) == 0:
            user_list.append(user)
    if len(user_list) > 0:
        await call.message.edit_text('Выберите пользователя')
        await call.message.edit_reply_markup(await select_unemployed_users_menu(user_list, data))
    else:
        await call.answer('Нет свободных работников')


@dp.callback_query_handler(add_user_to_department.filter())
async def add_user_to_department_method(call: CallbackQuery, state: FSMContext, callback_data: dict):
    id_user = callback_data.get('id')
    data = await state.get_data()
    await add_order(int(id_user), int(data['department_id']))
    workers = await select_workers_in_department(data['department_id'])
    await call.message.edit_text(f'Работники отдела ' + data['department_name'])
    await call.message.edit_reply_markup(await workers_menu(workers, data['department_id'], call.message.chat.id))


@dp.callback_query_handler(text_contains='employee_archive')
async def list_archive_users(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    users = await get_archive_users(int(data['department_id']))
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
async def worker_menu_method(call: CallbackQuery, callback_data: dict, state: FSMContext):
    id_user = callback_data.get('id')
    await state.update_data(user_id=id_user)
    name = callback_data.get('name')
    await call.message.edit_text(name + ' выбран')
    status = await get_worker(id_user)
    status = status[0]['status']
    await call.message.edit_reply_markup(await worker_menu(status, id_user, name, call.message.chat.id))


@dp.callback_query_handler(text_contains='backWorkerInDep')
async def add_worker_call(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    workers = await select_workers_in_department(data['department_id'])
    await call.message.edit_text(f'Работники отдела ' + data['department_name'])
    await call.message.edit_reply_markup(await workers_menu(workers, data['department_id'], call.message.chat.id))


async def show_worker(call, user_id, name):
    await call.message.edit_text(name + ' выбран')
    status = await get_worker(user_id)
    status = status[0]['status']
    await call.message.edit_reply_markup(await worker_menu(status, user_id, name, call.message.chat.id))


@dp.callback_query_handler(archive.filter())
async def archive_method(call: CallbackQuery, state: FSMContext, callback_data: dict):
    user_id = callback_data.get('id')
    await state.update_data(user_id=user_id)
    name = callback_data.get('name')
    await set_status_worker(user_id, 'archive')
    await show_worker(call, user_id, name)


@dp.callback_query_handler(unzip.filter())
async def unzip_method(call: CallbackQuery, callback_data: dict):
    user_id = callback_data.get('id')
    name = callback_data.get('name')
    await set_status_worker(user_id, 'worked')
    await show_worker(call, user_id, name)


@dp.callback_query_handler(add_pay.filter())
async def add_pay_method(call: CallbackQuery, state: FSMContext, callback_data: dict):
    call_data = await state.get_data()
    get_user = await get_user_role(int(call_data['department_id']), int(call_data['user_id']))
    if get_user[0]['status'] == 'archive':
        await call.answer('Пользователь в архиве!')
    else:
        await call.message.edit_text('Введите сумму')
        await Pay.enter_amount.set()


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


async def send_message_main_admin(msg, pay_id):
    print('+')
    for admin in ADMINS:
        print('+')
        await bot.send_message(admin, msg, reply_markup=send_request_main_admin(pay_id))


async def send_message_admin(bot_object, list_admins, msg, pay_id):
    for admin in list_admins:
        try:
            await bot.send_message(admin['user_id'], msg, reply_markup=send_request(pay_id))
        except Exception as e:
            await bot_object.answer('Кажется, ваш администратор удалил аккаунт!')


async def send_message_by_user(m, admins, msg, pay_id):
    if len(admins) == 0:
        await send_message_main_admin(msg, pay_id)
    elif len(admins) >= 1:
        await send_message_admin(m, admins, msg, pay_id)


async def accept_payment_main_admin(admin_telegram_id, pay_id):
    accept_pay = await update_status_pay(int(pay_id), 'Подтверждена главным администратором')
    get_pay = await get_pay_by_id(int(pay_id))
    user_id = int(get_pay[0]['user_id'])
    user_amount = get_pay[0]['amount']
    await bot.send_message(admin_telegram_id, 'Уведомление о оплате отправлено работнику')
    try:
        await bot.send_message(user_id, 'Вам оплачено <b>{}</b>.'.format(user_amount))
    except ChatNotFound:
        await bot.send_message('Уведомление о оплате пользователю не доставлено\nВозможно он остановил бота')


async def declined_payment_main_admin(admin_telegram_id, pay_id):
    accept_pay = await update_status_pay(int(pay_id), 'Подтверждена главным администратором')
    get_pay = await get_pay_by_id(int(pay_id))
    user_id = int(get_pay[0]['user_id'])
    user_amount = get_pay[0]['amount']
    await bot.send_message(admin_telegram_id, 'Уведомление о оплате отправлено работнику')
    try:
        await bot.send_message(user_id, 'Вам оплачено <b>{}</b>.'.format(user_amount))
    except ChatNotFound:
        await bot.send_message('Уведомление о оплате пользователю не доставлено\nВозможно он остановил бота')


def format_accept_message(pays):
    msg = f"Отправлен запрос на оплату\nСумма <code>{pays[0]['amount']}</code> \n" \
          f"Дата <code>{pays[0]['date']}</code>\n" \
          f"Название услуги <code>{pays[0]['name_service']}</code>\n" \
          f"Комментарий <code>{pays[0]['comment']}</code>"
    return msg


@dp.message_handler(state=Pay.enter_comment)
async def enter_comment(m: Message, state: FSMContext):
    data = await state.get_data()
    admins = await get_department_admin(int(data['department_id']))
    await state.finish()
    amount = data['amount']
    department_id = data['department_id']
    pays = await add_pay_for_user(int(data['user_id']), float(amount), data['name_service'], data['date'], m.text, 'Не подтверждена', int(department_id))
    pay_id = pays[0]['id']
    msg = format_accept_message(pays)
    if is_super_admin(m.chat.id):
        await accept_payment_main_admin(m.chat.id, pay_id)
    elif await is_admin(m.chat.id):
        await send_message_main_admin(msg, pay_id)
    elif await is_user(m.chat.id):
        await send_message_by_user(m, admins, msg, pay_id)
    await m.answer('Обновление данных, пожалуйста подождите')
    await update_spread()
    await m.answer(msg, reply_markup=await start_menu(await create_spread(), m.chat.id))


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


@dp.callback_query_handler(accept_request_pay.filter())
@dp.callback_query_handler(accept_request_pay_admin.filter())
async def accept_main_admin(call: CallbackQuery, state: FSMContext, callback_data: dict):
    pay_id = callback_data.get('pay_id')
    get_pay = await get_pay_by_id(int(pay_id))
    pay = get_pay[0]
    status_pay = get_pay[0]['status']
    if is_super_admin(call.message.chat.id):
        if status_pay in ['Отклонена', 'Подтверждена главным администратором']:
            await call.answer('Действие подтверждено ранее')
        else:
            await accept_payment_main_admin(call.message.chat.id, pay_id)
    else:
        if status_pay in ['Отклонена', 'Подтверждена главным администратором', 'Подтверждена руководителем']:
            await call.answer('Действие подтверждено ранее')
        else:
            accept_pay = await update_status_pay(int(pay_id), 'Подтверждена руководителем')
            msg = format_accept_message(get_pay)
            await send_message_main_admin(msg, pay_id)
            await call.answer('Действие подтверждено')


@dp.callback_query_handler(not_approved_pay.filter())
@dp.callback_query_handler(not_approved_pay_admin.filter())
async def not_approved_pay_admin(call: CallbackQuery, state: FSMContext, callback_data: dict):
    pay_id = callback_data.get('pay_id')
    get_pay = await get_pay_by_id(int(pay_id))
    status_pay = get_pay[0]['status']
    if is_super_admin(call.message.chat.id):
        if status_pay in ['Отклонена', 'Подтверждена главным администратором']:
            await call.answer('Действие подтверждено ранее')
        else:
            await call.answer('Введите комментарий:')
            await state.update_data(pay_id=pay_id)
            await Decline.comment.set()
    else:
        if status_pay in ['Отклонена', 'Подтверждена главным администратором', 'Подтверждена руководителем']:
            await call.answer('Действие подтверждено ранее')
        else:
            await call.answer('Введите комментарий:')
            await state.update_data(pay_id=pay_id)
            await Decline.comment.set()


@dp.message_handler(state=Decline.comment)
async def decline_pay_admin(message: Message, state: FSMContext):
    comment_admin = message.text
    data = await state.get_data()
    pay_id = data['pay_id']
    get_pay = await get_pay_by_id(int(pay_id))
    pay = get_pay[0]
    user_id = pay['user_id']
    get_user = await get_user_nickname(int(user_id))
    nickname = get_user[0]['nickname']
    admins = await get_department_admin(int(pay['department_id']))
    accept_pay = await update_status_pay(int(pay_id), 'Отклонена')
    if len(admins) >= 1 and is_super_admin(message.chat.id):
        send_mess = 'Оплата сотруднику {} отклонена главным админстратором.\nКомментарий администратора: {}' \
            .format(nickname, comment_admin)
        for admin in admins:
            try:
                await bot.send_message(int(admin['user_id']), send_mess)
            except:
                await message.answer('Сообщение об отмене не доставлена')
    else:
        send_mess = 'Оплата сотруднику {} отклонена руководителем.\nКомментарий руководителя: {}' \
            .format(nickname, comment_admin)
    await bot.send_message(user_id, send_mess)
    await bot.send_message(message.chat.id, 'Уведомление об отказе оплаты отправлено')







