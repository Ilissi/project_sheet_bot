from aiogram.dispatcher.filters.state import StatesGroup, State


class Decline(StatesGroup):
    comment = State()