from django.urls import path
from . import views

urlpatterns = [
    path("", views.task_list, name="task-list"),
    path("nova/", views.task_create, name="task-create"),
    path("<int:pk>/editar/", views.task_edit, name="task-edit"),
    path("<int:pk>/excluir/", views.task_delete, name="task-delete"),
    path("<int:pk>/concluir/", views.task_complete, name="task-complete"),
]