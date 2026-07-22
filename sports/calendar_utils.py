import calendar as pycalendar
from datetime import date
from .models import TrainingSession


def get_sports_month_calendar_data(year, month):
    first_day = date(year, month, 1)
    last_day_num = pycalendar.monthrange(year, month)[1]

    sessions = {
        s.date.day: s for s in TrainingSession.objects.filter(date__year=year, date__month=month)
    }

    days_status = {}
    for day in range(1, last_day_num + 1):
        session = sessions.get(day)
        if session is None:
            days_status[day] = "none"
        elif session.status == "foi":
            days_status[day] = "green"
        elif session.status == "nao_foi":
            days_status[day] = "red"
        else:
            days_status[day] = "yellow"

    cal = pycalendar.Calendar(firstweekday=6)
    weeks = cal.monthdayscalendar(year, month)

    return {
        "year": year,
        "month": month,
        "month_name": first_day.strftime("%B"),
        "weeks": weeks,
        "days_status": days_status,
    }
