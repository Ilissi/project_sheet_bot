from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from utils.db_api.users_controller import is_user, is_admin
from utils.db_api.utils import is_super_admin
from utils.google_sheet.spreed_methods import create_spread

from aiogram.types import CallbackQuery
from data import config
from loader import dp
from keyboards.inline.main_keyboard import start_menu



@dp.message_handler(commands=['start'], state='*')
async def status_bot(m: Message, state: FSMContext):
    if await is_user(m.chat.id) or await is_admin(m.chat.id):
        await state.finish()
        await m.answer('Меню', reply_markup=await start_menu(await create_spread(), m.chat.id))
    elif is_super_admin(m.chat.id):
        await state.finish()
        await m.answer('Меню', reply_markup=await start_menu(await create_spread(), m.chat.id))
    else:
        await m.answer('Вы не зарегистрированы в боте')


@dp.callback_query_handler(text_contains='back_main_menu', state='*',)
async def back_menu(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text('Меню')
    await call.message.edit_reply_markup(reply_markup=await start_menu(await create_spread(), call.message.chat.id))
