from django.urls import path
from . import views

urlpatterns = [
    path("", views.subject_list, name="subject-list"),
    path("nova/", views.subject_create, name="subject-create"),
    path("<int:pk>/", views.subject_detail, name="subject-detail"),
    path("tempo-estudado/novo/", views.studylog_create, name="studylog-create"),
    path("provas/nova/", views.exam_create, name="exam-create"),
    path("provas/<int:pk>/editar/", views.exam_edit, name="exam-edit"),
    path("trabalhos/novo/", views.assignment_create, name="assignment-create"),
    path("trabalhos/<int:pk>/editar/", views.assignment_edit, name="assignment-edit"),
    path("arquivos/novo/", views.studyfile_create, name="studyfile-create"),
]