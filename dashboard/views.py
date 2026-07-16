from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from tasks.models import Task

@login_required
def home(request):
    tasks = Task.objects.filter(status="pendente").order_by("due_date")
    return render(request, "dashboard/home.html", {"tasks": tasks})