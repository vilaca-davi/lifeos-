import calendar as pycalendar
from datetime import date
from .models import StudyLog, ExcusedDay


def get_month_calendar_data(year, month):
    today = date.today()
    first_day = date(year, month, 1)
    last_day_num = pycalendar.monthrange(year, month)[1]

    studied_dates = set(
        StudyLog.objects.filter(date__year=year, date__month=month).values_list("date", flat=True)
    )
    excused_dates = set(
        ExcusedDay.objects.filter(date__year=year, date__month=month).values_list("date", flat=True)
    )

    days_status = {}
    for day in range(1, last_day_num + 1):
        current = date(year, month, day)
        if current in studied_dates:
            days_status[day] = "green"
        elif current in excused_dates:
            days_status[day] = "yellow"
        elif current > today:
            days_status[day] = "future"
        else:
            days_status[day] = "red"

    cal = pycalendar.Calendar(firstweekday=0)
    weeks = cal.monthdayscalendar(year, month)

    return {
        "year": year,
        "month": month,
        "month_name": first_day.strftime("%B"),
        "weeks": weeks,
        "days_status": days_status,
    }