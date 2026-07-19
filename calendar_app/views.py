from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
import calendar as pycalendar
from datetime import datetime, date, timedelta
from .models import CalendarEvent
from .forms import CalendarEventForm
from .utils import get_occurrences
from django.urls import reverse
from studies.models import Exam, Assignment
from .google_calendar import export_event_to_google, import_events_from_google
from django.contrib import messages



@login_required
def calendar_month(request):
    today = timezone.localtime()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    first_day = date(year, month, 1)
    last_day_num = pycalendar.monthrange(year, month)[1]
    last_day = date(year, month, last_day_num)

    range_start = timezone.make_aware(datetime.combine(first_day, datetime.min.time()))
    range_end = timezone.make_aware(datetime.combine(last_day, datetime.max.time()))

    events = CalendarEvent.objects.all()

    days_events = {day: [] for day in range(1, last_day_num + 1)}

    # Eventos do próprio calendário (manuais, recorrentes etc.)
    for event in events:
        occurrences = get_occurrences(event, range_start, range_end)
        for occ in occurrences:
            local_occ = timezone.localtime(occ) if timezone.is_aware(occ) else occ
            if local_occ.year == year and local_occ.month == month:
                days_events[local_occ.day].append({
                    "title": event.title,
                    "when": local_occ,
                    "url": reverse("event-edit", args=[event.pk]),
                    "kind": "event",
                })

    # Provas do módulo de Estudos
    exams = Exam.objects.filter(date__gte=first_day, date__lte=last_day)
    for exam in exams:
        days_events[exam.date.day].append({
            "title": f"Prova: {exam.subject.name}",
            "when": None,
            "url": reverse("subject-detail", args=[exam.subject.pk]),
            "kind": "exam",
        })

    # Trabalhos do módulo de Estudos
    assignments = Assignment.objects.filter(due_date__gte=first_day, due_date__lte=last_day)
    for assignment in assignments:
        days_events[assignment.due_date.day].append({
            "title": f"Trabalho: {assignment.subject.name}",
            "when": None,
            "url": reverse("subject-detail", args=[assignment.subject.pk]),
            "kind": "assignment",
        })

    # Ordena os itens de cada dia: eventos com horário primeiro, depois provas/trabalhos
    for day in days_events:
        days_events[day].sort(key=lambda item: (item["when"] is None, item["when"]))

    cal = pycalendar.Calendar(firstweekday=0)
    weeks = cal.monthdayscalendar(year, month)

    prev_month = (month - 1) or 12
    prev_year = year if month > 1 else year - 1
    next_month = (month % 12) + 1
    next_year = year if month < 12 else year + 1

    return render(request, "calendar_app/calendar_month.html", {
        "year": year,
        "month": month,
        "month_name": first_day.strftime("%B"),
        "weeks": weeks,
        "days_events": days_events,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
        "today": today.date(),
    })

@login_required
def event_create(request):
    if request.method == "POST":
        form = CalendarEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.source = "manual"
            if event.is_recurring:
                event.show_in_upcoming = False
            event.save()

            if not event.is_recurring:
                try:
                    export_event_to_google(event)
                except Exception as e:
                    messages.warning(request, f"Evento salvo, mas não sincronizado com o Google: {e}")

            return redirect("calendar-month")
    else:
        form = CalendarEventForm()
    return render(request, "calendar_app/event_form.html", {"form": form})


@login_required
def event_edit(request, pk):
    event = get_object_or_404(CalendarEvent, pk=pk)
    if request.method == "POST":
        form = CalendarEventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save(commit=False)
            if event.is_recurring:
                event.show_in_upcoming = False
            event.save()

            if not event.is_recurring and event.source != "google":
                try:
                    export_event_to_google(event)
                except Exception as e:
                    messages.warning(request, f"Evento salvo, mas não sincronizado com o Google: {e}")

            return redirect("calendar-month")
    else:
        form = CalendarEventForm(instance=event)
    return render(request, "calendar_app/event_form.html", {"form": form})

@login_required
def event_delete(request, pk):
    event = get_object_or_404(CalendarEvent, pk=pk)
    if request.method == "POST":
        event.delete()
        return redirect("calendar-month")
    return render(request, "calendar_app/event_confirm_delete.html", {"event": event})

@login_required
def sync_google(request):
    try:
        count = import_events_from_google()
        messages.success(request, f"{count} evento(s) importado(s) do Google Agenda.")
    except Exception as e:
        messages.warning(request, f"Não foi possível sincronizar: {e}")
    return redirect("calendar-month")