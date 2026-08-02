from django.urls import path
from . import views

urlpatterns = [
    path("", views.sports_home, name="sports-home"),
    path("treino/novo/", views.session_create, name="session-create"),
    path("treino/<int:pk>/editar/", views.session_edit, name="session-edit"),
    path("treino/<int:pk>/excluir/", views.session_delete, name="session-delete"),
    path("competicao/nova/", views.competition_create, name="competition-create"),
    path("competicao/<int:pk>/editar/", views.competition_edit, name="competition-edit"),
    path("competicao/<int:pk>/excluir/", views.competition_delete, name="competition-delete"),
    path("calendario/", views.training_calendar, name="training-calendar"),
    path("calendario/marcar/", views.toggle_training, name="toggle-training"),
    path("competicao/<int:pk>/", views.competition_detail, name="competition-detail"),
    path("competicao/<int:competition_pk>/resultado/novo/", views.result_create, name="result-create"),
    path("resultado/<int:pk>/editar/", views.result_edit, name="result-edit"),
    path("resultado/<int:pk>/excluir/", views.result_delete, name="result-delete"),
    path("melhores-tempos/", views.best_times, name="best-times"),
    path("evolucao/", views.evolution_chart, name="evolution-chart"),
]