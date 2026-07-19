from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Avg
from .models import Subject, Exam, Assignment, StudyLog, StudyFile
from .forms import StudyLogForm, SubjectForm, ExamForm, AssignmentForm, StudyFileForm
from datetime import date, timedelta


@login_required
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, "studies/subject_list.html", {"subjects": subjects})


@login_required
@login_required
def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    exams = subject.exams.all()
    assignments = subject.assignments.all()
    study_logs = subject.study_logs.all()
    files = subject.files.all()

    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # segunda-feira desta semana
    end_of_week = start_of_week + timedelta(days=6)  # domingo desta semana

    weekly_minutes = study_logs.filter(
        date__gte=start_of_week, date__lte=end_of_week
    ).aggregate(total=Sum("minutes"))["total"] or 0

    average_grade = exams.exclude(grade__isnull=True).aggregate(avg=Avg("grade"))["avg"]

    return render(request, "studies/subject_detail.html", {
        "subject": subject,
        "exams": exams,
        "assignments": assignments,
        "study_logs": study_logs,
        "files": files,
        "weekly_minutes": weekly_minutes,
        "start_of_week": start_of_week,
        "end_of_week": end_of_week,
        "average_grade": average_grade,
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
def studyfile_create(request):
    if request.method == "POST":
        form = StudyFileForm(request.POST, request.FILES)
        if form.is_valid():
            study_file = form.save()
            return redirect("subject-detail", pk=study_file.subject.pk)
    else:
        form = StudyFileForm()
    return render(request, "studies/generic_form.html", {"form": form, "title": "Novo arquivo"})