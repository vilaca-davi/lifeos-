from django.urls import path
from . import api_views

urlpatterns = [
    # Tarefas
    path('tarefas/', api_views.api_tasks, name='api-tasks'),
    path('tarefas/<int:task_id>/concluir/', api_views.api_task_complete, name='api-task-complete'),
    
    # Estudos - Conteúdos
    path('estudos/conteudos/', api_views.api_study_content, name='api-study-content'),
    path('estudos/conteudos/<int:content_id>/atualizar/', api_views.api_study_content_update, name='api-study-content-update'),
    
    # Estudos - Provas
    path('estudos/provas/', api_views.api_exams, name='api-exams'),
    
    # Estudos - Trabalhos
    path('estudos/trabalhos/', api_views.api_assignments, name='api-assignments'),
    path('estudos/trabalhos/<int:assignment_id>/atualizar/', api_views.api_assignment_update, name='api-assignment-update'),
    
    # Esporte - Treinos
    path('esporte/treinos/', api_views.api_training_sessions, name='api-training-sessions'),
    path('esporte/treinos/<int:session_id>/atualizar/', api_views.api_training_session_update, name='api-training-session-update'),
    path('esporte/treinos/novo/', api_views.api_training_session_create, name='api-training-session-create'),
    
    # Esporte - Competições
    path('esporte/competicoes/', api_views.api_competitions, name='api-competitions'),
    path('esporte/competicoes/<int:competition_id>/', api_views.api_competition_detail, name='api-competition-detail'),
    
    # Esporte - Resultados
    path('esporte/resultados/novo/', api_views.api_swim_result_create, name='api-swim-result-create'),
    
    # Creatina
    path('creatina/', api_views.api_creatine_log, name='api-creatine-log'),
    path('creatina/marcar/', api_views.api_creatine_toggle, name='api-creatine-toggle'),
    
    # Calendário
    path('calendario/eventos/', api_views.api_calendar_events, name='api-calendar-events'),
    
    # Dashboard
    path('dashboard/resumo/', api_views.api_dashboard_summary, name='api-dashboard-summary'),

    path('tarefas/nova/', api_views.api_task_create, name='api-task-create'),
    path('tarefas/<int:task_id>/editar/', api_views.api_task_edit, name='api-task-edit'),
    path('tarefas/<int:task_id>/excluir/', api_views.api_task_delete, name='api-task-delete'),

    # Matérias
    path('estudos/materias/', api_views.api_subjects, name='api-subjects'),
    path('estudos/materias/nova/', api_views.api_subject_create, name='api-subject-create'),
    path('estudos/materias/<int:subject_id>/', api_views.api_subject_detail, name='api-subject-detail'),
    path('estudos/materias/<int:subject_id>/excluir/', api_views.api_subject_delete, name='api-subject-delete'),

    # Provas
    path('estudos/provas/nova/', api_views.api_exam_create, name='api-exam-create'),
    path('estudos/provas/<int:exam_id>/editar/', api_views.api_exam_edit, name='api-exam-edit'),
    path('estudos/provas/<int:exam_id>/excluir/', api_views.api_exam_delete, name='api-exam-delete'),

    # Trabalhos
    path('estudos/trabalhos/novo/', api_views.api_assignment_create, name='api-assignment-create'),
    path('estudos/trabalhos/<int:assignment_id>/editar/', api_views.api_assignment_edit, name='api-assignment-edit'),
    path('estudos/trabalhos/<int:assignment_id>/excluir/', api_views.api_assignment_delete, name='api-assignment-delete'),

    # Conteúdos
    path('estudos/conteudos/novo/', api_views.api_content_create, name='api-content-create'),
    path('estudos/conteudos/<int:content_id>/excluir/', api_views.api_content_delete, name='api-content-delete'),

    # Notas
    path('estudos/notas/nova/', api_views.api_grade_create, name='api-grade-create'),
    path('estudos/notas/<int:grade_id>/excluir/', api_views.api_grade_delete, name='api-grade-delete'),

    # Tempo estudado
    path('estudos/tempo/novo/', api_views.api_studylog_create, name='api-studylog-create'),

    path('tarefas/nova/', api_views.api_task_create, name='api-task-create'),
    path('tarefas/<int:task_id>/editar/', api_views.api_task_edit, name='api-task-edit'),
    path('tarefas/<int:task_id>/excluir/', api_views.api_task_delete, name='api-task-delete'),

]