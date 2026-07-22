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
    path("notas/nova/", views.grade_create, name="grade-create"),
    path("notas/<int:pk>/editar/", views.grade_edit, name="grade-edit"),
    path("notas/<int:pk>/excluir/", views.grade_delete, name="grade-delete"),
    path("conteudos/novo/", views.content_create, name="content-create"),
    path("conteudos/<int:pk>/editar/", views.content_edit, name="content-edit"),
    path("conteudos/<int:pk>/excluir/", views.content_delete, name="content-delete"),
    path("pomodoro/", views.pomodoro, name="pomodoro"),
    path("pomodoro/salvar/", views.pomodoro_save, name="pomodoro-save"),
    path("calendario/", views.study_calendar, name="study-calendar"),
    path("calendario/desculpa/", views.toggle_excuse, name="toggle-excuse"),
    path("provas/<int:pk>/excluir/", views.exam_delete, name="exam-delete"),
    path("trabalhos/<int:pk>/excluir/", views.assignment_delete, name="assignment-delete"),
    path("tempo-estudado/", views.study_time_detail, name="study-time-detail"),
]