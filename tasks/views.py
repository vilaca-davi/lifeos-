from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from .forms import TaskForm


@login_required
def task_list(request):
    tasks = Task.objects.all().order_by("status", "due_date")

    status = request.GET.get("status")
    priority = request.GET.get("priority")

    if status:
        tasks = tasks.filter(status=status)
    if priority:
        tasks = tasks.filter(priority=priority)

    return render(request, "tasks/task_list.html", {
        "tasks": tasks,
        "status_choices": Task.STATUS_CHOICES,
        "priority_choices": Task.PRIORITY_CHOICES,
        "selected_status": status,
        "selected_priority": priority,
    })

@login_required
def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("task-list")
    else:
        form = TaskForm()
    return render(request, "tasks/task_form.html", {"form": form})

@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("task-list")
    else:
        form = TaskForm(instance=task)
    return render(request, "tasks/task_form.html", {"form": form})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        task.delete()
        return redirect("task-list")
    return render(request, "tasks/task_confirm_delete.html", {"task": task})

@login_required
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.status = "concluida"
    task.save()

    if task.source_key and task.source_key.startswith("creatine:"):
        from creatine.models import CreatineLog
        day = task.source_key.split("creatine:")[1]
        from datetime import date
        target_date = date.fromisoformat(day)
        CreatineLog.objects.get_or_create(date=target_date)

    # Sincronização: mochila → entregue
    if task.source_key and task.source_key.startswith("assignment:") and ":mochila" in task.source_key:
        from studies.models import Assignment
        assignment_id = int(task.source_key.split(":")[1])
        assignment = Assignment.objects.filter(pk=assignment_id).first()
        if assignment:
            assignment.status = "entregue"
            assignment.save()

    # NOVA SINCRONIZAÇÃO: conteúdos estudados
    if task.source_key and task.source_key.startswith("studycontent:"):
        from studies.models import StudyContent, StudyLog
        from datetime import date
        parts = task.source_key.split(":")
        content_id = int(parts[1])
        action = parts[2] if len(parts) > 2 else None
        
        content = StudyContent.objects.filter(pk=content_id).first()
        if content:
            if action == "estudar":
                content.status = "estudado"
                content.save()
                # Registra no calendário de estudos (1 minuto de tempo)
                StudyLog.objects.get_or_create(
                    subject=content.subject,
                    date=date.today(),
                    defaults={"minutes": 1}
                )
            elif action == "revisar":
                content.status = "revisado"
                content.save()
                # Registra no calendário de estudos
                StudyLog.objects.get_or_create(
                    subject=content.subject,
                    date=date.today(),
                    defaults={"minutes": 1}
                )
            elif action == "anki":
                content.questions_done = True
                content.save()

    return redirect(request.META.get("HTTP_REFERER", "task-list"))