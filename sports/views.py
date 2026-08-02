from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, timedelta
from .models import TrainingSession, Competition, SwimResult
from .forms import TrainingSessionForm, CompetitionForm, SwimResultForm
from .calendar_utils import get_sports_month_calendar_data
from creatine.calendar_utils import get_creatine_month_calendar_data
from django.db.models import Min
from django.http import JsonResponse


@login_required
def sports_home(request):
    today = date.today()
    calendar_data = get_sports_month_calendar_data(today.year, today.month)
    creatine_calendar_data = get_creatine_month_calendar_data(today.year, today.month)
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
        "creatine_calendar_data": creatine_calendar_data,
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
            competition = form.save()
            return redirect("competition-detail", pk=competition.pk)
    else:
        form = CompetitionForm(initial={"date": date.today()})
    return render(request, "sports/generic_form.html", {"form": form, "title": "Nova competição"})


@login_required
def competition_detail(request, pk):
    competition = get_object_or_404(Competition, pk=pk)
    results = competition.results.all()
    return render(request, "sports/competition_detail.html", {"competition": competition, "results": results})


@login_required
def result_create(request, competition_pk):
    competition = get_object_or_404(Competition, pk=competition_pk)
    if request.method == "POST":
        form = SwimResultForm(request.POST, initial={"competition": competition})
        if form.is_valid():
            form.save()
            return redirect("competition-detail", pk=competition.pk)
    else:
        form = SwimResultForm(initial={"competition": competition})
    return render(request, "sports/generic_form.html", {"form": form, "title": "Novo resultado"})


@login_required
def result_edit(request, pk):
    result = get_object_or_404(SwimResult, pk=pk)
    if request.method == "POST":
        form = SwimResultForm(request.POST, instance=result)
        if form.is_valid():
            form.save()
            return redirect("competition-detail", pk=result.competition.pk)
    else:
        form = SwimResultForm(instance=result)
    return render(request, "sports/generic_form.html", {"form": form, "title": "Editar resultado"})


@login_required
def result_delete(request, pk):
    result = get_object_or_404(SwimResult, pk=pk)
    competition_pk = result.competition.pk
    if request.method == "POST":
        result.delete()
        return redirect("competition-detail", pk=competition_pk)
    return render(request, "sports/result_confirm_delete.html", {"result": result})

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

        return redirect(f"/esportes/calendario/?year={year}&month={month}")
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


@login_required
def best_times(request):
    best = (
        SwimResult.objects
        .values("event")
        .annotate(best_time=Min("time_centiseconds"))
        .order_by("event")
    )

    results = []
    for item in best:
        record = SwimResult.objects.filter(
            event=item["event"], time_centiseconds=item["best_time"]
        ).select_related("competition").first()
        results.append(record)

    return render(request, "sports/best_times.html", {"results": results})


@login_required
def evolution_chart(request):
    from sports.models import SwimResult
    
    events = SwimResult.EVENT_CHOICES
    selected_event = request.GET.get("event", events[0][0] if events else None)
    period = request.GET.get("period", "all")  # "all" ou "year"
    
    results = SwimResult.objects.filter(event=selected_event).select_related("competition").order_by("competition__date")
    
    if period == "year":
        from datetime import timedelta
        one_year_ago = date.today() - timedelta(days=365)
        results = results.filter(competition__date__gte=one_year_ago)
    
    # Calcula estatísticas
    best_time = results.aggregate(Min("time_centiseconds"))["time_centiseconds__min"]
    first_time = results.first().time_centiseconds if results.exists() else None
    improvement = first_time - best_time if first_time and best_time else 0
    count = results.count()
    
    def format_time(cs):
        minutes = cs // 6000
        seconds = (cs % 6000) // 100
        centiseconds = cs % 100
        return f"{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
    
    # Monta dados pro gráfico
    chart_data = [
        {
            "date": r.competition.date.strftime("%d/%m/%Y"),
            "time": r.time_centiseconds,
            "timeFormatted": format_time(r.time_centiseconds),
            "competition": r.competition.name or "Competição",
        }
        for r in results
    ]
    
    return render(request, "sports/evolution_chart.html", {
        "events": events,
        "selected_event": selected_event,
        "period": period,
        "chart_data": chart_data,
        "best_time": format_time(best_time) if best_time else "—",
        "improvement": format_time(improvement) if improvement > 0 else "—",
        "count": count,
        "first_time": format_time(first_time) if first_time else "—",
    })