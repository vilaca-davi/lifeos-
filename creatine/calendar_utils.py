import calendar as pycalendar
from datetime import date
from .models import CreatineLog


def get_creatine_month_calendar_data(year, month):
    first_day = date(year, month, 1)
    last_day_num = pycalendar.monthrange(year, month)[1]

    taken_dates = set(
        CreatineLog.objects.filter(date__year=year, date__month=month).values_list("date", flat=True)
    )

    days_status = {}
    for day in range(1, last_day_num + 1):
        current = date(year, month, day)
        days_status[day] = "green" if current in taken_dates else "red"

    cal = pycalendar.Calendar(firstweekday=6)
    weeks = cal.monthdayscalendar(year, month)

    return {
        "year": year,
        "month": month,
        "month_name": first_day.strftime("%B"),
        "weeks": weeks,
        "days_status": days_status,
    }