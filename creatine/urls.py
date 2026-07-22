from django.urls import path
from . import views

urlpatterns = [
    path("", views.creatine_calendar, name="creatine-calendar"),
    path("marcar/", views.toggle_creatine, name="toggle-creatine"),
]