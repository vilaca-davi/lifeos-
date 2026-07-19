from django.urls import path
from . import views

urlpatterns = [
    path("", views.subject_list, name="subject-list"),
    path("<int:pk>/", views.subject_detail, name="subject-detail"),
    path("tempo-estudado/novo/", views.studylog_create, name="studylog-create"),
]