from aiogram.dispatcher.filters.state import StatesGroup, State


class Pay(StatesGroup):
    enter_amount = State()
    enter_name_service = State()
    enter_date = State()
    enter_comment = State()