from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Avg
from .models import Subject, Exam, Assignment, StudyLog, StudyFile
from .forms import StudyLogForm


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
    files = subject.files.all()

    total_minutes = study_logs.aggregate(total=Sum("minutes"))["total"] or 0
    average_grade = exams.exclude(grade__isnull=True).aggregate(avg=Avg("grade"))["avg"]

    return render(request, "studies/subject_detail.html", {
        "subject": subject,
        "exams": exams,
        "assignments": assignments,
        "study_logs": study_logs,
        "files": files,
        "total_minutes": total_minutes,
        "average_grade": average_grade,
    })


@login_required
def studylog_create(request):
    if request.method == "POST":
        form = StudyLogForm(request.POST)
        if form.is_valid():
            log = form.save()
            return redirect("subject-detail", pk=log.subject.pk)
    else:
        form = StudyLogForm()
    return render(request, "studies/studylog_form.html", {"form": form})