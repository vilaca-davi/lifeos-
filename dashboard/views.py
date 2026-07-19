from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import date, timedelta
from tasks.models import Task
from studies.models import Exam, Assignment


@login_required
def home(request):
    tasks = Task.objects.filter(status="pendente").order_by("due_date")

    today = date.today()
    horizon = today + timedelta(days=14)  # próximas 2 semanas

    upcoming_exams = Exam.objects.filter(
        date__gte=today, date__lte=horizon
    ).order_by("date")

    upcoming_assignments = Assignment.objects.filter(
        due_date__gte=today, due_date__lte=horizon
    ).exclude(status="entregue").order_by("due_date")

    return render(request, "dashboard/home.html", {
        "tasks": tasks,
        "upcoming_exams": upcoming_exams,
        "upcoming_assignments": upcoming_assignments,
    })