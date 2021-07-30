from aiogram.dispatcher.filters.state import StatesGroup, State


class Departments(StatesGroup):
    enter_name = State()