from aiogram.dispatcher.filters.state import StatesGroup, State


class Users(StatesGroup):
    enter_name = State()
    enter_id = State()
    enter_permissions = State()
    add_project_to_user = State()