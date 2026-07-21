from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Avg
from datetime import date, timedelta
from .models import Subject, Exam, Assignment, StudyLog, Grade, StudyContent
from .forms import StudyLogForm, SubjectForm, ExamForm, AssignmentForm, GradeForm, StudyContentForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
import calendar as pycalendar
from .models import ExcusedDay
from .calendar_utils import get_month_calendar_data


def calculate_streak():
    dates = set(StudyLog.objects.values_list("date", flat=True))
    if not dates:
        return 0

    today = date.today()
    if today in dates:
        current = today
    elif (today - timedelta(days=1)) in dates:
        current = today - timedelta(days=1)
    else:
        return 0

    streak = 0
    while current in dates:
        streak += 1
        current -= timedelta(days=1)

    return streak


@login_required
def subject_list(request):
    subjects = Subject.objects.all()

    total_minutes = StudyLog.objects.aggregate(total=Sum("minutes"))["total"] or 0
    study_streak = calculate_streak()
    contents_to_study = StudyContent.objects.filter(status="falta_estudar").select_related("subject")
    contents_to_review = StudyContent.objects.filter(status="estudado").select_related("subject")

    today = date.today()
    calendar_data = get_month_calendar_data(today.year, today.month)

    return render(request, "studies/subject_list.html", {
        "subjects": subjects,
        "total_minutes": total_minutes,
        "study_streak": study_streak,
        "contents_to_study": contents_to_study,
        "contents_to_review": contents_to_review,
        "calendar_data": calendar_data,
    })


@login_required
def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    exams = subject.exams.all()
    assignments = subject.assignments.all()
    study_logs = subject.study_logs.all()

    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    weekly_minutes = study_logs.filter(
        date__gte=start_of_week, date__lte=end_of_week
    ).aggregate(total=Sum("minutes"))["total"] or 0

    grades = subject.grades.all()
    contents = subject.contents.all()

    bimester_totals = {}
    for b in [1, 2, 3, 4]:
        total = grades.filter(bimester=b).aggregate(total=Sum("value"))["total"]
        bimester_totals[b] = total

    valid_bimesters = [v for v in bimester_totals.values() if v is not None]
    year_total = sum(valid_bimesters) if valid_bimesters else None

    return render(request, "studies/subject_detail.html", {
        "subject": subject,
        "exams": exams,
        "assignments": assignments,
        "study_logs": study_logs,
        "weekly_minutes": weekly_minutes,
        "start_of_week": start_of_week,
        "end_of_week": end_of_week,
        "grades": grades,
        "bimester_totals": bimester_totals,
        "year_total": year_total,
        "contents": contents,
    })


@login_required
def subject_create(request):
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            return redirect("subject-detail", pk=subject.pk)
    else:
        form = SubjectForm()
    return render(request, "studies/generic_form.html", {"form": form, "title": "Nova matéria"})


@login_required
def studylog_create(request):
    if request.method == "POST":
        form = StudyLogForm(request.POST)
        if form.is_valid():
            log = form.save()
            return redirect("subject-detail", pk=log.subject.pk)
    else:
        form = StudyLogForm()
    return render(request, "studies/generic_form.html", {"form": form, "title": "Registrar tempo estudado"})


@login_required
def exam_create(request):
    if request.method == "POST":
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save()
            return redirect("subject-detail", pk=exam.subject.pk)
    else:
        form = ExamForm()
    return render(request, "studies/generic_form.html", {"form": form, "title": "Nova prova"})


@login_required
def exam_edit(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == "POST":
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            return redirect("subject-detail", pk=exam.subject.pk)
    else:
        form = ExamForm(instance=exam)
    return render(request, "studies/generic_form.html", {"form": form, "title": "Editar prova"})


@login_required
def assignment_create(request):
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save()
            return redirect("subject-detail", pk=assignment.subject.pk)
    else:
        form = AssignmentForm()
    return render(request, "studies/generic_form.html", {"form": form, "title": "Novo trabalho"})


@login_required
def assignment_edit(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            return redirect("subject-detail", pk=assignment.subject.pk)
    else:
        form = AssignmentForm(instance=assignment)
    return render(request, "studies/generic_form.html", {"form": form, "title": "Editar trabalho"})


@login_required
def grade_create(request):
    if request.method == "POST":
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save()
            return redirect("subject-detail", pk=grade.subject.pk)
    else:
        form = GradeForm()
    return render(request, "studies/generic_form.html", {"form": form, "title": "Nova nota"})


@login_required
def grade_edit(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    if request.method == "POST":
        form = GradeForm(request.POST, instance=grade)
        if form.is_valid():
            form.save()
            return redirect("subject-detail", pk=grade.subject.pk)
    else:
        form = GradeForm(instance=grade)
    return render(request, "studies/generic_form.html", {"form": form, "title": "Editar nota"})


@login_required
def grade_delete(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    subject_pk = grade.subject.pk
    if request.method == "POST":
        grade.delete()
        return redirect("subject-detail", pk=subject_pk)
    return render(request, "studies/grade_confirm_delete.html", {"grade": grade})



@login_required
def content_create(request):
    if request.method == "POST":
        form = StudyContentForm(request.POST)
        if form.is_valid():
            content = form.save()
            return redirect("subject-detail", pk=content.subject.pk)
    else:
        form = StudyContentForm()
    return render(request, "studies/generic_form.html", {"form": form, "title": "Novo conteúdo"})


@login_required
def content_edit(request, pk):
    content = get_object_or_404(StudyContent, pk=pk)
    if request.method == "POST":
        form = StudyContentForm(request.POST, instance=content)
        if form.is_valid():
            form.save()
            return redirect("subject-detail", pk=content.subject.pk)
    else:
        form = StudyContentForm(instance=content)
    return render(request, "studies/generic_form.html", {"form": form, "title": "Editar conteúdo"})


@login_required
def content_delete(request, pk):
    content = get_object_or_404(StudyContent, pk=pk)
    subject_pk = content.subject.pk
    if request.method == "POST":
        content.delete()
        return redirect("subject-detail", pk=subject_pk)
    return render(request, "studies/content_confirm_delete.html", {"content": content})


@login_required
def pomodoro(request):
    subjects = Subject.objects.all()
    return render(request, "studies/pomodoro.html", {"subjects": subjects})


@login_required
@require_POST
def pomodoro_save(request):
    subject_id = request.POST.get("subject_id")
    minutes = request.POST.get("minutes")

    try:
        subject = Subject.objects.get(pk=subject_id)
        minutes = int(minutes)
        if minutes <= 0:
            raise ValueError
    except (Subject.DoesNotExist, ValueError, TypeError):
        return JsonResponse({"ok": False, "error": "Dados inválidos."}, status=400)

    StudyLog.objects.create(subject=subject, date=date.today(), minutes=minutes)
    return JsonResponse({"ok": True, "subject": subject.name, "minutes": minutes})


@login_required
def study_calendar(request):
    today = date.today()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    calendar_data = get_month_calendar_data(year, month)

    prev_month = (month - 1) or 12
    prev_year = year if month > 1 else year - 1
    next_month = (month % 12) + 1
    next_year = year if month < 12 else year + 1

    return render(request, "studies/study_calendar.html", {
        "calendar_data": calendar_data,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
    })
    return render(request, "studies/study_calendar.html", data)


@login_required
def toggle_excuse(request):
    if request.method == "POST":
        day_str = request.POST.get("date")
        year = request.POST.get("year")
        month = request.POST.get("month")
        try:
            target_date = date.fromisoformat(day_str)
        except (ValueError, TypeError):
            return redirect("study-calendar")

        excused = ExcusedDay.objects.filter(date=target_date).first()
        if excused:
            excused.delete()
        else:
            ExcusedDay.objects.create(date=target_date)

        return redirect(f"/estudos/calendario/?year={year}&month={month}")
    return redirect("study-calendar")


@login_required
def study_time_detail(request):
    subject_id = request.GET.get("subject")

    logs = StudyLog.objects.select_related("subject").order_by("-date")
    selected_subject = None

    if subject_id:
        selected_subject = get_object_or_404(Subject, pk=subject_id)
        logs = logs.filter(subject=selected_subject)

    total_minutes = logs.aggregate(total=Sum("minutes"))["total"] or 0

    by_subject = None
    if not selected_subject:
        by_subject = (
            StudyLog.objects.values("subject__id", "subject__name")
            .annotate(total=Sum("minutes"))
            .order_by("-total")
        )

    return render(request, "studies/study_time_detail.html", {
        "logs": logs,
        "total_minutes": total_minutes,
        "selected_subject": selected_subject,
        "by_subject": by_subject,
    })


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