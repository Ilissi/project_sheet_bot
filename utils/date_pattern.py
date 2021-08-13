from datetime import datetime


def check_date(line):
    try:
        two_date_str = line.split('/')
        one_date = two_date_str[0].split('-')
        second_date = two_date_str[1].split('-')
        one_datetime = datetime(int(one_date[2]), int(one_date[1]), int(one_date[0]))
        second_datetime = datetime(int(second_date[2]), int(second_date[1]), int(second_date[0]))
        return True
    except:
        return False


def get_delta(line):
    two_date_str = line.split('/')
    one_date = two_date_str[0].split('-')
    second_date = two_date_str[1].split('-')
    one_datetime = datetime(int(one_date[2]),int(one_date[1]),int(one_date[0]))
    second_datetime = datetime(int(second_date[2]),int(second_date[1]),int(second_date[0]))
    return [one_datetime,second_datetime]


def to_datetime(line):
    date = line.split('-')
    return datetime(int(date[2]),int(date[1]),int(date[0]))