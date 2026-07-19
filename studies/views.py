from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Avg
from datetime import date, timedelta
from .models import Subject, Exam, Assignment, StudyLog, Grade, StudyContent
from .forms import StudyLogForm, SubjectForm, ExamForm, AssignmentForm, GradeForm, StudyContentForm


@login_required
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, "studies/subject_list.html", {"subjects": subjects})


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