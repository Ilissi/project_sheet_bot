from aiogram.types import CallbackQuery

from utils.db_api.order_controller import add_pay
from utils.google_sheet.spreed_methods import create_spread, update_spread
from loader import dp, bot
from data import config
from utils.callback import accept_request_pay, not_approved_pay
from keyboards.inline.main_keyboard import start_menu


@dp.callback_query_handler(accept_request_pay.filter())
async def request_control_menu(call: CallbackQuery, callback_data: dict):
    id_user = callback_data.get('i')
    amount = callback_data.get('a')
    date = callback_data.get('d')
    name_service = callback_data.get('n')
    data_call = callback_data.get('c').rsplit('*',maxsplit=1)
    comment = data_call[0]
    department_id = int(data_call[1])
    msg = f"Одобрен запрос на оплату\n\n " \
          f"ID юзера {id_user}\n" \
          f"Сумма <code>{amount}</code> \n" \
          f"Дата <code>{date}</code>\n" \
          f"Название услуги <code>{name_service}</code>\n" \
          f"Комментарий <code>{comment}</code>"
    print(id_user)
    await update_spread()
    await add_pay(int(id_user), float(amount), name_service, date, comment,department_id)
    await bot.send_message(config.admin, msg)
    await bot.send_message(id_user,
                           f"Одобрен запрос на оплату\nДата <code>{date}</code>\nКомментарий <code>{comment}</code>")
    await call.message.edit_text('✅')
    await call.message.edit_reply_markup(await start_menu(create_spread(), call.message.chat.id))


@dp.callback_query_handler(not_approved_pay.filter())
async def not_approved_method(call: CallbackQuery, callback_data: dict):
    id_user = callback_data.get('id_user')
    date = callback_data.get('date')
    comment = callback_data.get('comment')
    msg = f"Отклонен запрос на оплату\n\n " \
          f"Дата <code>{date}</code>\n" \
          f"Комментарий <code>{comment}</code>"
    await bot.send_message(int(id_user), msg)
    await call.message.edit_text('❌')
    await call.message.edit_reply_markup(await start_menu(create_spread(), call.message.chat.id))
