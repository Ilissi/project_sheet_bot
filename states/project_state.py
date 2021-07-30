from aiogram.dispatcher.filters.state import StatesGroup, State


class Projects(StatesGroup):
    enter_name = State()
    enter_admin = State()