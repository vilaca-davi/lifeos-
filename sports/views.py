from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, timedelta
from .models import TrainingSession, Competition
from .forms import TrainingSessionForm, CompetitionForm
from .calendar_utils import get_sports_month_calendar_data


@login_required
def sports_home(request):
    today = date.today()
    calendar_data = get_sports_month_calendar_data(today.year, today.month)
    competitions = Competition.objects.all()

    last_8_weeks_start = today - timedelta(weeks=8)
    recent_sessions = TrainingSession.objects.filter(date__gte=last_8_weeks_start).exclude(status="desculpa")
    total_recent = recent_sessions.count()
    attended_recent = recent_sessions.filter(status="foi").count()
    attendance_rate = round((attended_recent / total_recent) * 100) if total_recent else None

    return render(request, "sports/sports_home.html", {
        "calendar_data": calendar_data,
        "competitions": competitions,
        "attendance_rate": attendance_rate,
        "attended_recent": attended_recent,
        "total_recent": total_recent,
    })


@login_required
def session_create(request):
    if request.method == "POST":
        form = TrainingSessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("sports-home")
    else:
        form = TrainingSessionForm(initial={"date": date.today()})
    return render(request, "sports/generic_form.html", {"form": form, "title": "Registrar treino"})


@login_required
def session_edit(request, pk):
    session = get_object_or_404(TrainingSession, pk=pk)
    if request.method == "POST":
        form = TrainingSessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            return redirect("sports-home")
    else:
        form = TrainingSessionForm(instance=session)
    return render(request, "sports/generic_form.html", {"form": form, "title": "Editar treino"})


@login_required
def session_delete(request, pk):
    session = get_object_or_404(TrainingSession, pk=pk)
    if request.method == "POST":
        session.delete()
        return redirect("sports-home")
    return render(request, "sports/session_confirm_delete.html", {"session": session})


@login_required
def competition_create(request):
    if request.method == "POST":
        form = CompetitionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("sports-home")
    else:
        form = CompetitionForm(initial={"date": date.today()})
    return render(request, "sports/generic_form.html", {"form": form, "title": "Nova competição"})


@login_required
def competition_edit(request, pk):
    competition = get_object_or_404(Competition, pk=pk)
    if request.method == "POST":
        form = CompetitionForm(request.POST, instance=competition)
        if form.is_valid():
            form.save()
            return redirect("sports-home")
    else:
        form = CompetitionForm(instance=competition)
    return render(request, "sports/generic_form.html", {"form": form, "title": "Editar competição"})


@login_required
def competition_delete(request, pk):
    competition = get_object_or_404(Competition, pk=pk)
    if request.method == "POST":
        competition.delete()
        return redirect("sports-home")
    return render(request, "sports/competition_confirm_delete.html", {"competition": competition})


@login_required
def training_calendar(request):
    today = date.today()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    calendar_data = get_sports_month_calendar_data(year, month)

    prev_month = (month - 1) or 12
    prev_year = year if month > 1 else year - 1
    next_month = (month % 12) + 1
    next_year = year if month < 12 else year + 1

    return render(request, "sports/training_calendar.html", {
        "calendar_data": calendar_data,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
    })


@login_required
def toggle_training(request):
    if request.method == "POST":
        day_str = request.POST.get("date")
        year = request.POST.get("year")
        month = request.POST.get("month")
        try:
            target_date = date.fromisoformat(day_str)
        except (ValueError, TypeError):
            return redirect("training-calendar")

        session = TrainingSession.objects.filter(date=target_date).first()
        if session is None:
            TrainingSession.objects.create(date=target_date, status="foi")
        elif session.status == "foi":
            session.status = "nao_foi"
            session.save()
        elif session.status == "nao_foi":
            session.status = "desculpa"
            session.save()
        else:
            session.delete()

        return redirect(f"/esporte/calendario/?year={year}&month={month}")
    return redirect("training-calendar")


@login_required
def exam_delete(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    subject_pk = exam.subject.pk
    if request.method == "POST":
        exam.delete()
        return redirect("subject-detail", pk=subject_pk)
    return render(request, "studies/exam_confirm_delete.html", {"exam": exam})


@login_required
def assignment_delete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    subject_pk = assignment.subject.pk
    if request.method == "POST":
        assignment.delete()
        return redirect("subject-detail", pk=subject_pk)
    return render(request, "studies/assignment_confirm_delete.html", {"assignment": assignment})