from django.urls import path
from . import views

urlpatterns = [
    path("", views.calendar_month, name="calendar-month"),
    path("novo/", views.event_create, name="event-create"),
    path("<int:pk>/editar/", views.event_edit, name="event-edit"),
    path("<int:pk>/excluir/", views.event_delete, name="event-delete"),
]