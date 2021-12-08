import datetime


def last_day_of_current_month():
    next_month = datetime.date.today().replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)

def first_day_of_current_month():
    first_day_of_month = datetime.date.today().replace(day=1)
    return first_day_of_month

def first_day_of_next_month():
    first_day_of_month = datetime.date.today().replace(day=1)
    next_month=first_day_of_month.month+1
    year = first_day_of_month.year
    if next_month > 12:
        next_month = 1
        year = year + 1
    first_day_of_month = first_day_of_month.replace(month=next_month, year=year)
    return first_day_of_month

def today():
    return datetime.date.today()
