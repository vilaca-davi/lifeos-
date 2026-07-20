from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from datetime import date, timedelta
from tasks.models import Task
from studies.models import Exam, Assignment
from studies.calendar_utils import get_month_calendar_data
from calendar_app.models import CalendarEvent


@login_required
def home(request):
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    from django.db.models import Q
    tasks = Task.objects.filter(status="pendente").filter(
        Q(due_date__gte=start_of_week, due_date__lte=end_of_week) | Q(due_date__isnull=True)
    ).order_by("due_date")

    horizon = today + timedelta(days=14)

    upcoming_exams = Exam.objects.filter(
        date__gte=today, date__lte=horizon
    ).order_by("date")

    upcoming_assignments = Assignment.objects.filter(
        due_date__gte=today, due_date__lte=horizon
    ).exclude(status="entregue").order_by("due_date")

    now = timezone.localtime()
    horizon_datetime = now + timedelta(days=14)

    upcoming_events = CalendarEvent.objects.filter(
        show_in_upcoming=True,
        start_datetime__gte=now,
        start_datetime__lte=horizon_datetime,
    ).order_by("start_datetime")

    calendar_data = get_month_calendar_data(today.year, today.month)

    return render(request, "dashboard/home.html", {
        "tasks": tasks,
        "upcoming_exams": upcoming_exams,
        "upcoming_assignments": upcoming_assignments,
        "upcoming_events": upcoming_events,
        "calendar_data": calendar_data,
    })