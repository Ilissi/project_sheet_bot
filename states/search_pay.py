from aiogram.dispatcher.filters.state import StatesGroup, State


class Search(StatesGroup):
    enter_date = State()
