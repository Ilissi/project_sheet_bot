import math

from utils.db_api.department_controllers import get_departments
from utils.db_api.project_controllers import select_all_projects
from utils.db_api.spread_controllers import insert_spread, get_spread_page, get_spread, get_spreadsheet, \
    update_spreadsheet
from utils.google_sheet import Spreedsheet, spreedsheet_utils

from data import config
import asyncio


async def create_spread():
    ss = Spreedsheet.Spreadsheet(config.GOOGLE_CREDENTIALS_FILE, debugMode=False)
    spread = await get_spreadsheet()
    project = await select_all_projects()
    if len(spread) == 0 and len(project) != 0:
        first_project = project[0]
        new_spread = spreedsheet_utils.create_spreadsheet(ss, first_project['name'])
        await update_spreadsheet(new_spread['spreadsheetId'])
        await insert_spread(new_spread['sheetId'], new_spread['sheetTitle'], 1, first_project['id'])
    elif len(project) == 0:
        return 'N'
    else:
        spreadsheet = await get_spreadsheet()
        ss.setSpreadsheetById(spreadsheet[0]['spreadsheet_id'])
    return ss.getSheetURL()


async def update_spread():
    spread = await get_spreadsheet()
    projects = await select_all_projects()
    for project in projects:
        fields = await get_departments(project['id'])  # Получили отделы
        month_list = await spreedsheet_utils.get_month_list(fields)
        pages = math.ceil((len(month_list) / 6))
        if pages == 1 and project['id'] == 1:
            await spreedsheet_utils.create_first_page(spread[0]['spreadsheet_id'], project['id'])
        else:
            spread_id = await get_spread(project['id'])
            if len(spread_id) == 0:
                pages = 1
                sheet = spreedsheet_utils.create_new_sheet(spread[0]['spreadsheet_id'], project['name'])
                await spreedsheet_utils.create_new_page(project['id'], spread[0]['spreadsheet_id'], sheet['sheetId'], sheet['sheetTitle'],
                                                        month_list)
                await insert_spread(sheet['sheetId'], sheet['sheetTitle'], pages, project['id'])
            else:
                first_index = 0
                second_index = 6
                for iter_page in range(1, pages + 1):
                    page = await get_spread_page(project['id'], iter_page)
                    if len(page) == 0:
                        set_month = month_list[first_index:second_index]
                        sheet = spreedsheet_utils.create_new_sheet(spread[0]['spreadsheet_id'], '{} лист №{}'.format(project['name'], iter_page))
                        await spreedsheet_utils.create_new_page(project['id'], spread[0]['spreadsheet_id'], sheet['sheetId'],
                                                                sheet['sheetTitle'], set_month)
                        await insert_spread(sheet['sheetId'], sheet['sheetTitle'], iter_page, project['id'])
                    else:
                        spreedsheet_utils.clear_sheet(spread[0]['spreadsheet_id'], page[0]['sheetId'], page[0]['sheetTitle'])
                        await spreedsheet_utils.create_new_page(project['id'], spread[0]['spreadsheet_id'], page[0]['sheetId'],
                                                                page[0]['sheetTitle'], set_month)
                    first_index += 6
                    second_index += 6



