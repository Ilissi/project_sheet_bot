from datetime import datetime
import locale
import time

from utils.db_api.department_controllers import get_departments_pay, get_departments
from utils.db_api.order_controller import get_sum, get_user_pay
from utils.db_api.project_controllers import get_project_name
from utils.db_api.users_controller import get_user_id, select_user
from utils.google_sheet import Spreedsheet
from data import config


def generate_word(date_value):
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    d = datetime.strptime(date_value, "%m-%Y")
    return d.strftime('%b %Y год.')


def draw_month(ss, month_list):
    counter = 0
    for month in month_list:
        add_month(ss, generate_word(month), counter)
        counter += 4


def column(matrix, i):
    return '\n'.join([str(row[i]) for row in matrix])


def create_spreadsheet(ss, name_of_project):
    spreadsheetId = ss.create("Таблица", name_of_project)
    ss.shareWithEmailForWriting(config.email)
    return spreadsheetId


def add_month(ss, date_string, value, first_symbol='A', second_symbol='D'):
    set_value = '{}1:{}2'.format(chr(ord(first_symbol) + value), chr(ord(second_symbol) + value))
    format_dict = {'horizontalAlignment': 'CENTER',
                   'textFormat': {'fontSize': 28, 'fontFamily': 'Times New Roman'}}
    set_string = '{}1'.format(chr(ord(first_symbol) + value))
    ss.prepare_mergeCells(set_value)
    ss.prepare_setCellsFormat(set_value, format_dict)
    ss.prepare_setValues(set_string, [[date_string]])
    ss.runPrepared()


def add_department(ss, department_name, value, index_first, first_symbol='A', second_symbol='D'):
    set_value = '{}{}:{}{}'.format(chr(ord(first_symbol) + value), index_first,
                                   chr(ord(second_symbol) + value), index_first + 1, )
    set_department_name = '{}{}'.format(chr(ord(first_symbol) + value), index_first)
    set_field = '{}{}:{}{}'.format(chr(ord(first_symbol) + value), index_first + 2,
                                   chr(ord(second_symbol) + value), index_first + 2, )
    set_field_name = ['Работник', 'Оплата', 'Дата', 'Комментарий']
    format_dict = {'horizontalAlignment': 'CENTER',
                   'textFormat': {'fontSize': 28, 'fontFamily': 'Times New Roman'}}
    ss.prepare_mergeCells(set_value)
    ss.prepare_setCellsFormat(set_value, format_dict)
    ss.prepare_setValues(set_department_name, [[department_name]])
    ss.prepare_setValues(set_field, [set_field_name])
    ss.runPrepared()


def add_user_without_pays(ss, pays_value, value, index_first, first_symbol='A'):
    set_field = '{}{}'.format(chr(ord(first_symbol) + value), index_first + 2)
    ss.prepare_setValues(set_field, [[pays_value]])
    ss.runPrepared()


def add_user_with_pay(ss, username, pays_list, value, index_first, first_symbol='A', second_symbol='D'):
    set_field = '{}{}:{}{}'.format(chr(ord(first_symbol) + value), index_first + 2,
                                   chr(ord(second_symbol) + value), index_first + 2, )
    print(set_field)
    set_list = [username, column(pays_list, 1), column(pays_list, 2), column(pays_list, 3)]
    ss.prepare_setValues(set_field, [set_list])
    ss.runPrepared()


async def get_month_list(fields_list):
    month_list = []
    for field in fields_list:
        pays = await get_departments_pay(field['id'])
        for pay in pays:
            month_year = pay['date'][3:11]
            if month_year not in month_list:
                month_list.append(month_year)
    month_list.sort(key=lambda record: datetime.strptime(record, "%m-%Y"))
    return month_list


def add_sum(ss, name, amount, value, index_first, index_add, first_symbol='A', second_symbol='D'):
    set_field = '{}{}:{}{}'.format(chr(ord(first_symbol) + value), index_first + index_add,
                                   chr(ord(second_symbol) + value), index_first + index_add,)
    set_list = ['Итого по {}'.format(name), amount]
    ss.prepare_setValues(set_field, [set_list])
    ss.runPrepared()


async def get_department_sum(field, month):
    count_of_pays = await get_sum(field['id'])
    department_sum = 0
    for pay in count_of_pays:
        if month in pay['date']:
            department_sum += pay['amount']
    return department_sum


async def get_project_sum(project_id, month):
    fields = await get_departments(project_id)
    project_sum = 0
    for field in fields:
        project_sum += await get_department_sum(field, month)
    return project_sum


async def draw_page(ss, project_id, fields, month_list):
    draw_month(ss, month_list)
    time.sleep(4)
    counter_value_column = 0
    for month in month_list:
        counter_value_row = 3
        for field in fields:
            add_department(ss, field['department_name'], counter_value_column, counter_value_row)
            users = await get_user_id(field['id'])
            for user in set(users):
                list_with_pays = []
                counter_value_row += 1
                pays = await get_user_pay(field['id'], user['user_id'])
                time.sleep(4)
                get_user_username = await select_user(user['user_id'])
                username = get_user_username[0]['nickname']
                for pay in pays:
                    if month in pay['date']:
                        list_with_pays.append(pay)
                if len(list_with_pays) == 0:
                    add_user_without_pays(ss, username, counter_value_column, counter_value_row)
                else:
                    add_pays = []
                    for pay in list_with_pays:
                        add_pays.append([values for values in pay.values()])
                    add_user_with_pay(ss, username, add_pays, counter_value_column, counter_value_row)
                time.sleep(1)
            department_sum = await get_department_sum(field, month)
            add_sum(ss, field['department_name'], department_sum, counter_value_column, counter_value_row, 3)
            counter_value_row += 1
            counter_value_row += 4
        project_sum = await get_project_sum(project_id, month)
        project_name = await get_project_name(project_id)
        add_sum(ss, project_name[0]['project_name'], project_sum, counter_value_column, counter_value_row, 0)
        counter_value_column += 4


async def clear_sheet(spreadsheetId, sheetId, sheetTitle):
    ss = Spreedsheet.Spreadsheet(config.GOOGLE_CREDENTIALS_FILE, debugMode=False)
    ss.setSpreadsheetBy(spreadsheetId, sheetId, sheetTitle)
    ss.clear_table()
    ss.prepare_mergeCells('A1:Z1000')
    ss.prepare_unmergeCells('A1:Z1000')
    ss.runPrepared()


async def create_first_page(spread_id, project_id):
    ss = Spreedsheet.Spreadsheet(config.GOOGLE_CREDENTIALS_FILE, debugMode=False)
    ss.setSpreadsheetById(spread_id)
    fields = await get_departments(project_id)  # Получили отделы
    month_list = await get_month_list(fields)
    await draw_page(ss, project_id, fields, month_list)


async def create_new_page(project_id, spreadsheetId, sheetId, sheetTitle, month_list):
    ss = Spreedsheet.Spreadsheet(config.GOOGLE_CREDENTIALS_FILE, debugMode=False)
    ss.setSpreadsheetBy(spreadsheetId, sheetId, sheetTitle)
    fields = await get_departments(project_id)  # Получили отделы
    await draw_page(ss, project_id, fields, month_list)


def create_new_sheet(spread_id, title_name):
    ss = Spreedsheet.Spreadsheet(config.GOOGLE_CREDENTIALS_FILE, debugMode=False)
    ss.setSpreadsheetById(spread_id)
    return ss.addSheet(title_name)
