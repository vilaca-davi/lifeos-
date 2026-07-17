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
    return redirect(request.META.get("HTTP_REFERER", "task-list"))