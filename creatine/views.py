from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from datetime import date
from .models import CreatineLog
from .calendar_utils import get_creatine_month_calendar_data


@login_required
def creatine_calendar(request):
    today = date.today()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    calendar_data = get_creatine_month_calendar_data(year, month)

    prev_month = (month - 1) or 12
    prev_year = year if month > 1 else year - 1
    next_month = (month % 12) + 1
    next_year = year if month < 12 else year + 1

    return render(request, "creatine/creatine_calendar.html", {
        "calendar_data": calendar_data,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
    })


@login_required
def toggle_creatine(request):
    if request.method == "POST":
        day_str = request.POST.get("date")
        year = request.POST.get("year")
        month = request.POST.get("month")
        try:
            target_date = date.fromisoformat(day_str)
        except (ValueError, TypeError):
            return redirect("creatine-calendar")

        log = CreatineLog.objects.filter(date=target_date).first()
        if log:
            log.delete()
        else:
            CreatineLog.objects.create(date=target_date)

        return redirect(f"/creatina/?year={year}&month={month}")
    return redirect("creatine-calendar")