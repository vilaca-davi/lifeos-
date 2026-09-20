from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from datetime import date, timedelta
from .models import Task
from studies.models import StudyContent, Exam, Assignment, StudyLog
from sports.models import TrainingSession, Competition, SwimResult
from creatine.models import CreatineLog
from calendar_app.models import CalendarEvent

# TAREFAS
@require_http_methods(["GET"])
def api_tasks(request):
    status = request.GET.get('status', 'pendente')
    tasks = Task.objects.filter(status=status).values(
        'id', 'title', 'due_date', 'priority', 'status'
    ).order_by('-due_date')
    return JsonResponse({'tasks': list(tasks)})

@require_http_methods(["POST"])
@csrf_exempt
def api_task_complete(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        task.status = 'concluida'
        task.save()
        return JsonResponse({'success': True, 'task_id': task_id})
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)

# ESTUDOS - CONTEÚDOS
@require_http_methods(["GET"])
def api_study_content(request):
    subject_id = request.GET.get('subject')
    contents = StudyContent.objects.all()
    if subject_id:
        contents = contents.filter(subject_id=subject_id)
    contents = contents.values(
        'id', 'title', 'status', 'subject__id', 'subject__name', 'questions_done'
    ).order_by('status')
    return JsonResponse({'contents': list(contents)})

@require_http_methods(["POST"])
@csrf_exempt
def api_study_content_update(request, content_id):
    try:
        from tasks.generators import complete_auto_task
        content = StudyContent.objects.get(id=content_id)
        status = request.POST.get('status')
        if status:
            content.status = status
        questions_done = request.POST.get('questions_done')
        if questions_done:
            content.questions_done = questions_done == 'true'
        content.save()
        
        # Sincronizar tarefas
        if content.status in ("estudado", "revisado"):
            complete_auto_task(f"studycontent:{content.pk}:estudar")
        if content.status == "revisado":
            complete_auto_task(f"studycontent:{content.pk}:revisar")
        if content.questions_done:
            complete_auto_task(f"studycontent:{content.pk}:anki")
        
        # Registrar estudo no calendário
        from datetime import date
        StudyLog.objects.get_or_create(
            subject=content.subject,
            date=date.today(),
            defaults={'minutes': 1}
        )
        
        return JsonResponse({'success': True, 'content_id': content_id})
    except StudyContent.DoesNotExist:
        return JsonResponse({'error': 'Content not found'}, status=404)

# ESTUDOS - PROVAS
@require_http_methods(["GET"])
def api_exams(request):
    subject_id = request.GET.get('subject')
    exams = Exam.objects.all()
    if subject_id:
        exams = exams.filter(subject_id=subject_id)
    exams = exams.values(
        'id', 'title', 'date', 'subject__id', 'subject__name'
    ).order_by('date')
    return JsonResponse({'exams': list(exams)})

# ESTUDOS - TRABALHOS
@require_http_methods(["GET"])
def api_assignments(request):
    subject_id = request.GET.get('subject')
    assignments = Assignment.objects.exclude(status='entregue')
    if subject_id:
        assignments = assignments.filter(subject_id=subject_id)
    assignments = assignments.values(
        'id', 'due_date', 'status', 'description', 'subject__id', 'subject__name'
    ).order_by('due_date')
    return JsonResponse({'assignments': list(assignments)})

@require_http_methods(["POST"])
@csrf_exempt
def api_assignment_update(request, assignment_id):
    try:
        from tasks.generators import complete_auto_task
        assignment = Assignment.objects.get(id=assignment_id)
        status = request.POST.get('status')
        if status:
            assignment.status = status
            assignment.save()
            
            # Sincronizar tarefas
            if status in ("iniciado", "concluido", "entregue"):
                complete_auto_task(f"assignment:{assignment.pk}:iniciar")
            if status in ("concluido", "entregue"):
                complete_auto_task(f"assignment:{assignment.pk}:concluir")
        
        return JsonResponse({'success': True, 'assignment_id': assignment_id})
    except Assignment.DoesNotExist:
        return JsonResponse({'error': 'Assignment not found'}, status=404)

# ESPORTE - TREINOS
@require_http_methods(["GET"])
def api_training_sessions(request):
    month = request.GET.get('month')
    year = request.GET.get('year')
    sessions = TrainingSession.objects.all()
    if month and year:
        sessions = sessions.filter(date__month=int(month), date__year=int(year))
    sessions = sessions.values(
        'id', 'date', 'status', 'notes'
    ).order_by('-date')
    return JsonResponse({'sessions': list(sessions)})

@require_http_methods(["POST"])
@csrf_exempt
def api_training_session_update(request, session_id):
    try:
        session = TrainingSession.objects.get(id=session_id)
        status = request.POST.get('status')
        if status:
            session.status = status
            session.save()
        return JsonResponse({'success': True, 'session_id': session_id})
    except TrainingSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)

@require_http_methods(["POST"])
@csrf_exempt
def api_training_session_create(request):
    try:
        training_date = request.POST.get('date')
        status = request.POST.get('status', 'foi')
        notes = request.POST.get('notes', '')
        session, created = TrainingSession.objects.get_or_create(
            date=training_date,
            defaults={'status': status, 'notes': notes}
        )
        if not created:
            session.status = status
            session.notes = notes
            session.save()
        return JsonResponse({'success': True, 'session_id': session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# ESPORTE - COMPETIÇÕES
@require_http_methods(["GET"])
def api_competitions(request):
    month = request.GET.get('month')
    year = request.GET.get('year')
    comps = Competition.objects.all()
    if month and year:
        comps = comps.filter(date__month=int(month), date__year=int(year))
    comps = comps.values(
        'id', 'date', 'name', 'club'
    ).order_by('-date')
    return JsonResponse({'competitions': list(comps)})

@require_http_methods(["GET"])
def api_competition_detail(request, competition_id):
    try:
        comp = Competition.objects.get(id=competition_id)
        results = SwimResult.objects.filter(competition_id=competition_id).values(
            'id', 'event', 'time_centiseconds', 'placement'
        )
        return JsonResponse({
            'competition': {
                'id': comp.id,
                'date': str(comp.date),
                'name': comp.name,
                'club': comp.club,
            },
            'results': list(results)
        })
    except Competition.DoesNotExist:
        return JsonResponse({'error': 'Competition not found'}, status=404)

# ESPORTE - RESULTADOS
@require_http_methods(["POST"])
@csrf_exempt
def api_swim_result_create(request):
    try:
        competition_id = request.POST.get('competition_id')
        event = request.POST.get('event')
        time_str = request.POST.get('time')  # MM:SS.CC
        placement = request.POST.get('placement')
        
        # Converter MM:SS.CC pra centésimos
        parts = time_str.split(':')
        minutes = int(parts[0])
        sec_parts = parts[1].split('.')
        seconds = int(sec_parts[0])
        centiseconds = int(sec_parts[1])
        time_centiseconds = minutes * 6000 + seconds * 100 + centiseconds
        
        result = SwimResult.objects.create(
            competition_id=competition_id,
            event=event,
            time_centiseconds=time_centiseconds,
            placement=int(placement) if placement else None
        )
        return JsonResponse({'success': True, 'result_id': result.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# CREATINA
@require_http_methods(["GET"])
def api_creatine_log(request):
    month = request.GET.get('month')
    year = request.GET.get('year')
    logs = CreatineLog.objects.all()
    if month and year:
        logs = logs.filter(date__month=int(month), date__year=int(year))
    logs = logs.values('id', 'date').order_by('-date')
    return JsonResponse({'logs': list(logs)})

@require_http_methods(["POST"])
@csrf_exempt
def api_creatine_toggle(request):
    try:
        from datetime import date
        target_date = request.POST.get('date')
        log = CreatineLog.objects.filter(date=target_date).first()
        if log:
            log.delete()
            # Atualizar tarefa
            Task.objects.filter(
                source_key=f"creatine:{target_date}"
            ).update(status='pendente')
            return JsonResponse({'success': True, 'action': 'deleted'})
        else:
            CreatineLog.objects.create(date=target_date)
            # Atualizar tarefa
            Task.objects.filter(
                source_key=f"creatine:{target_date}"
            ).update(status='concluida')
            return JsonResponse({'success': True, 'action': 'created'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# CALENDÁRIO
@require_http_methods(["GET"])
def api_calendar_events(request):
    month = request.GET.get('month')
    year = request.GET.get('year')
    events = CalendarEvent.objects.filter(show_in_upcoming=True)
    if month and year:
        events = events.filter(
            start_datetime__month=int(month),
            start_datetime__year=int(year)
        )
    events = events.values(
        'id', 'title', 'start_datetime', 'end_datetime', 'source'
    ).order_by('start_datetime')
    return JsonResponse({'events': list(events)})

# DASHBOARD - RESUMO DO DIA
@require_http_methods(["GET"])
def api_dashboard_summary(request):
    today = date.today()
    
    # Tarefas do dia
    tasks_today = Task.objects.filter(
        due_date=today,
        status='pendente'
    ).count()
    
    # Próximas provas (7 dias)
    horizon = today + timedelta(days=7)
    exams_upcoming = Exam.objects.filter(
        date__gte=today,
        date__lte=horizon
    ).count()
    
    # Próximos trabalhos
    assignments_upcoming = Assignment.objects.filter(
        due_date__gte=today,
        status__in=['pendente', 'iniciado']
    ).count()
    
    # Treinos (últimas 8 semanas)
    last_8_weeks = today - timedelta(weeks=8)
    sessions = TrainingSession.objects.filter(date__gte=last_8_weeks)
    attended = sessions.filter(status='foi').count()
    total = sessions.exclude(status='desculpa').count()
    attendance_rate = round((attended / total) * 100) if total > 0 else 0
    
    # Creatina hoje
    creatine_today = CreatineLog.objects.filter(date=today).exists()
    
    return JsonResponse({
        'tasks_today': tasks_today,
        'exams_upcoming': exams_upcoming,
        'assignments_upcoming': assignments_upcoming,
        'attendance_rate': attendance_rate,
        'creatine_today': creatine_today,
    })



@require_http_methods(["POST"])
@csrf_exempt
def api_task_create(request):
    try:
        title = request.POST.get('title')
        due_date = request.POST.get('due_date') or None
        priority = request.POST.get('priority', 'media')
        
        if not title:
            return JsonResponse({'error': 'Título obrigatório'}, status=400)
        
        task = Task.objects.create(
            title=title,
            due_date=due_date,
            priority=priority,
            status='pendente',
        )
        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'due_date': str(task.due_date) if task.due_date else None,
                'priority': task.priority,
                'status': task.status,
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def api_task_delete(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        task.delete()
        return JsonResponse({'success': True})
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Tarefa não encontrada'}, status=404)


@require_http_methods(["POST"])
@csrf_exempt
def api_task_edit(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        title = request.POST.get('title')
        due_date = request.POST.get('due_date') or None
        priority = request.POST.get('priority')
        status = request.POST.get('status')
        
        if title: task.title = title
        if due_date is not None: task.due_date = due_date
        if priority: task.priority = priority
        if status: task.status = status
        task.save()
        
        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'due_date': str(task.due_date) if task.due_date else None,
                'priority': task.priority,
                'status': task.status,
            }
        })
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Tarefa não encontrada'}, status=404)
    


# ESTUDOS - MATÉRIAS
@require_http_methods(["GET"])
def api_subjects(request):
    from studies.models import Subject, StudyLog
    from django.db.models import Sum
    from datetime import date, timedelta
    
    subjects = Subject.objects.all()
    result = []
    
    for subject in subjects:
        # Tempo total
        total_minutes = StudyLog.objects.filter(
            subject=subject
        ).aggregate(total=Sum('minutes'))['total'] or 0
        
        # Streak
        streak = 0
        check_date = date.today()
        while StudyLog.objects.filter(subject=subject, date=check_date).exists():
            streak += 1
            check_date -= timedelta(days=1)
        
        result.append({
            'id': subject.id,
            'name': subject.name,
            'total_minutes': total_minutes,
            'streak': streak,
        })
    
    return JsonResponse({'subjects': result})


@require_http_methods(["POST"])
@csrf_exempt
def api_subject_create(request):
    from studies.models import Subject
    try:
        name = request.POST.get('name')
        if not name:
            return JsonResponse({'error': 'Nome obrigatório'}, status=400)
        subject = Subject.objects.create(name=name)
        return JsonResponse({'success': True, 'subject': {'id': subject.id, 'name': subject.name}})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def api_subject_delete(request, subject_id):
    from studies.models import Subject
    try:
        Subject.objects.get(id=subject_id).delete()
        return JsonResponse({'success': True})
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Matéria não encontrada'}, status=404)


# ESTUDOS - DETALHE DA MATÉRIA
@require_http_methods(["GET"])
def api_subject_detail(request, subject_id):
    from studies.models import Subject, StudyLog, Grade, StudyContent, Exam, Assignment
    from django.db.models import Sum
    from datetime import date, timedelta
    
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Matéria não encontrada'}, status=404)
    
    # Tempo semana
    start_of_week = date.today() - timedelta(days=date.today().weekday())
    end_of_week = start_of_week + timedelta(days=6)
    weekly_minutes = StudyLog.objects.filter(
        subject=subject,
        date__gte=start_of_week,
        date__lte=end_of_week
    ).aggregate(total=Sum('minutes'))['total'] or 0
    
    # Notas por bimestre
    bimester_totals = {}
    for b in range(1, 5):
        total = Grade.objects.filter(
            subject=subject, bimester=b
        ).aggregate(total=Sum('value'))['total'] or 0
        bimester_totals[str(b)] = float(total)
    
    year_total = sum(bimester_totals.values())
    
    # Notas
    grades = list(Grade.objects.filter(subject=subject).values(
        'id', 'type', 'description', 'value', 'bimester', 'date'
    ).order_by('-date'))
    
    # Provas
    exams = list(Exam.objects.filter(subject=subject).values(
        'id', 'title', 'date', 'content'
    ).order_by('date'))
    
    # Trabalhos
    assignments = list(Assignment.objects.filter(subject=subject).values(
        'id', 'due_date', 'description', 'status'
    ).order_by('due_date'))
    
    # Conteúdos
    contents = list(StudyContent.objects.filter(subject=subject).values(
        'id', 'title', 'status', 'questions_done'
    ).order_by('status'))
    
    return JsonResponse({
        'subject': {'id': subject.id, 'name': subject.name},
        'weekly_minutes': weekly_minutes,
        'bimester_totals': bimester_totals,
        'year_total': year_total,
        'grades': grades,
        'exams': exams,
        'assignments': assignments,
        'contents': contents,
    })


# ESTUDOS - PROVAS CRUD
@require_http_methods(["POST"])
@csrf_exempt
def api_exam_create(request):
    from studies.models import Exam, Subject
    try:
        subject_id = request.POST.get('subject_id')
        title = request.POST.get('title', '')
        date_str = request.POST.get('date')
        content = request.POST.get('content', '')
        
        exam = Exam.objects.create(
            subject_id=subject_id,
            title=title,
            date=date_str,
            content=content,
        )
        return JsonResponse({'success': True, 'exam': {
            'id': exam.id, 'title': exam.title, 'date': str(exam.date)
        }})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def api_exam_edit(request, exam_id):
    from studies.models import Exam
    try:
        exam = Exam.objects.get(id=exam_id)
        if request.POST.get('title') is not None:
            exam.title = request.POST.get('title')
        if request.POST.get('date'):
            exam.date = request.POST.get('date')
        if request.POST.get('content') is not None:
            exam.content = request.POST.get('content')
        exam.save()
        return JsonResponse({'success': True})
    except Exam.DoesNotExist:
        return JsonResponse({'error': 'Prova não encontrada'}, status=404)


@require_http_methods(["POST"])
@csrf_exempt
def api_exam_delete(request, exam_id):
    from studies.models import Exam
    try:
        Exam.objects.get(id=exam_id).delete()
        return JsonResponse({'success': True})
    except Exam.DoesNotExist:
        return JsonResponse({'error': 'Prova não encontrada'}, status=404)


# ESTUDOS - TRABALHOS CRUD
@require_http_methods(["POST"])
@csrf_exempt
def api_assignment_create(request):
    from studies.models import Assignment, Subject
    try:
        subject_id = request.POST.get('subject_id')
        due_date = request.POST.get('due_date')
        description = request.POST.get('description', '')
        
        assignment = Assignment.objects.create(
            subject_id=subject_id,
            due_date=due_date,
            description=description,
            status='pendente',
        )
        return JsonResponse({'success': True, 'assignment': {
            'id': assignment.id,
            'due_date': str(assignment.due_date),
            'status': assignment.status,
        }})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def api_assignment_edit(request, assignment_id):
    from studies.models import Assignment
    from tasks.generators import complete_auto_task
    try:
        assignment = Assignment.objects.get(id=assignment_id)
        if request.POST.get('due_date'):
            assignment.due_date = request.POST.get('due_date')
        if request.POST.get('description') is not None:
            assignment.description = request.POST.get('description')
        if request.POST.get('status'):
            assignment.status = request.POST.get('status')
            if assignment.status in ('iniciado', 'concluido', 'entregue'):
                complete_auto_task(f"assignment:{assignment.pk}:iniciar")
            if assignment.status in ('concluido', 'entregue'):
                complete_auto_task(f"assignment:{assignment.pk}:concluir")
        assignment.save()
        return JsonResponse({'success': True})
    except Assignment.DoesNotExist:
        return JsonResponse({'error': 'Trabalho não encontrado'}, status=404)


@require_http_methods(["POST"])
@csrf_exempt
def api_assignment_delete(request, assignment_id):
    from studies.models import Assignment
    try:
        Assignment.objects.get(id=assignment_id).delete()
        return JsonResponse({'success': True})
    except Assignment.DoesNotExist:
        return JsonResponse({'error': 'Trabalho não encontrado'}, status=404)


# ESTUDOS - CONTEÚDOS CRUD
@require_http_methods(["POST"])
@csrf_exempt
def api_content_create(request):
    from studies.models import StudyContent, Subject
    try:
        subject_id = request.POST.get('subject_id')
        title = request.POST.get('title')
        if not title:
            return JsonResponse({'error': 'Título obrigatório'}, status=400)
        content = StudyContent.objects.create(
            subject_id=subject_id,
            title=title,
            status='falta_estudar',
        )
        return JsonResponse({'success': True, 'content': {
            'id': content.id, 'title': content.title, 'status': content.status
        }})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def api_content_delete(request, content_id):
    from studies.models import StudyContent
    try:
        StudyContent.objects.get(id=content_id).delete()
        return JsonResponse({'success': True})
    except StudyContent.DoesNotExist:
        return JsonResponse({'error': 'Conteúdo não encontrado'}, status=404)


# ESTUDOS - NOTAS CRUD
@require_http_methods(["POST"])
@csrf_exempt
def api_grade_create(request):
    from studies.models import Grade, Subject
    try:
        grade = Grade.objects.create(
            subject_id=request.POST.get('subject_id'),
            type=request.POST.get('type', 'prova'),
            description=request.POST.get('description', ''),
            value=float(request.POST.get('value', 0)),
            bimester=int(request.POST.get('bimester', 1)),
            date=request.POST.get('date'),
        )
        return JsonResponse({'success': True, 'grade': {
            'id': grade.id, 'value': float(grade.value), 'bimester': grade.bimester
        }})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def api_grade_delete(request, grade_id):
    from studies.models import Grade
    try:
        Grade.objects.get(id=grade_id).delete()
        return JsonResponse({'success': True})
    except Grade.DoesNotExist:
        return JsonResponse({'error': 'Nota não encontrada'}, status=404)


# ESTUDOS - TEMPO
@require_http_methods(["POST"])
@csrf_exempt
def api_studylog_create(request):
    from studies.models import StudyLog, Subject
    try:
        StudyLog.objects.create(
            subject_id=request.POST.get('subject_id'),
            date=request.POST.get('date'),
            minutes=int(request.POST.get('minutes', 0)),
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["POST"])
@csrf_exempt
def api_task_create(request):
    try:
        title = request.POST.get('title')
        due_date = request.POST.get('due_date') or None
        priority = request.POST.get('priority', 'media')
        
        if not title:
            return JsonResponse({'error': 'Título obrigatório'}, status=400)
        
        task = Task.objects.create(
            title=title,
            due_date=due_date,
            priority=priority,
            status='pendente',
        )
        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'due_date': str(task.due_date) if task.due_date else None,
                'priority': task.priority,
                'status': task.status,
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def api_task_delete(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        task.delete()
        return JsonResponse({'success': True})
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Tarefa não encontrada'}, status=404)


@require_http_methods(["POST"])
@csrf_exempt
def api_task_edit(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        title = request.POST.get('title')
        due_date = request.POST.get('due_date') or None
        priority = request.POST.get('priority')
        status = request.POST.get('status')
        
        if title: task.title = title
        if due_date is not None: task.due_date = due_date
        if priority: task.priority = priority
        if status: task.status = status
        task.save()
        
        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'due_date': str(task.due_date) if task.due_date else None,
                'priority': task.priority,
                'status': task.status,
            }
        })
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Tarefa não encontrada'}, status=404)


# ESTUDOS - MATÉRIAS
@require_http_methods(["GET"])
def api_subjects(request):
    from studies.models import Subject, StudyLog
    from django.db.models import Sum
    from datetime import date, timedelta
    
    subjects = Subject.objects.all()
    result = []
    
    for subject in subjects:
        # Tempo total
        total_minutes = StudyLog.objects.filter(
            subject=subject
        ).aggregate(total=Sum('minutes'))['total'] or 0
        
        # Streak
        streak = 0
        check_date = date.today()
        while StudyLog.objects.filter(subject=subject, date=check_date).exists():
            streak += 1
            check_date -= timedelta(days=1)
        
        result.append({
            'id': subject.id,
            'name': subject.name,
            'total_minutes': total_minutes,
            'streak': streak,
        })
    
    return JsonResponse({'subjects': result})


@require_http_methods(["POST"])
@csrf_exempt
def api_subject_create(request):
    from studies.models import Subject
    try:
        name = request.POST.get('name')
        if not name:
            return JsonResponse({'error': 'Nome obrigatório'}, status=400)
        subject = Subject.objects.create(name=name)
        return JsonResponse({'success': True, 'subject': {'id': subject.id, 'name': subject.name}})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def api_subject_delete(request, subject_id):
    from studies.models import Subject
    try:
        Subject.objects.get(id=subject_id).delete()
        return JsonResponse({'success': True})
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Matéria não encontrada'}, status=404)


# ESTUDOS - DETALHE DA MATÉRIA
@require_http_methods(["GET"])
def api_subject_detail(request, subject_id):
    from studies.models import Subject, StudyLog, Grade, StudyContent, Exam, Assignment
    from django.db.models import Sum
    from datetime import date, timedelta
    
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Matéria não encontrada'}, status=404)
    
    # Tempo semana
    start_of_week = date.today() - timedelta(days=date.today().weekday())
    end_of_week = start_of_week + timedelta(days=6)
    weekly_minutes = StudyLog.objects.filter(
        subject=subject,
        date__gte=start_of_week,
        date__lte=end_of_week
    ).aggregate(total=Sum('minutes'))['total'] or 0
    
    # Notas por bimestre
    bimester_totals = {}
    for b in range(1, 5):
        total = Grade.objects.filter(
            subject=subject, bimester=b
        ).aggregate(total=Sum('value'))['total'] or 0
        bimester_totals[str(b)] = float(total)
    
    year_total = sum(bimester_totals.values())
    
    # Notas
    grades = list(Grade.objects.filter(subject=subject).values(
        'id', 'type', 'description', 'value', 'bimester', 'date'
    ).order_by('-date'))
    
    # Provas
    exams = list(Exam.objects.filter(subject=subject).values(
        'id', 'title', 'date', 'content'
    ).order_by('date'))
    
    # Trabalhos
    assignments = list(Assignment.objects.filter(subject=subject).values(
        'id', 'due_date', 'description', 'status'
    ).order_by('due_date'))
    
    # Conteúdos
    contents = list(StudyContent.objects.filter(subject=subject).values(
        'id', 'title', 'status', 'questions_done'
    ).order_by('status'))
    
    return JsonResponse({
        'subject': {'id': subject.id, 'name': subject.name},
        'weekly_minutes': weekly_minutes,
        'bimester_totals': bimester_totals,
        'year_total': year_total,
        'grades': grades,
        'exams': exams,
        'assignments': assignments,
        'contents': contents,
    })


# ESTUDOS - PROVAS CRUD
@require_http_methods(["POST"])
@csrf_exempt
def api_exam_create(request):
    from studies.models import Exam, Subject
    try:
        subject_id = request.POST.get('subject_id')
        title = request.POST.get('title', '')
        date_str = request.POST.get('date')
        content = request.POST.get('content', '')
        
        exam = Exam.objects.create(
            subject_id=subject_id,
            title=title,
            date=date_str,
            content=content,
        )
        return JsonResponse({'success': True, 'exam': {
            'id': exam.id, 'title': exam.title, 'date': str(exam.date)
        }})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def api_exam_edit(request, exam_id):
    from studies.models import Exam
    try:
        exam = Exam.objects.get(id=exam_id)
        if request.POST.get('title') is not None:
            exam.title = request.POST.get('title')
        if request.POST.get('date'):
            exam.date = request.POST.get('date')
        if request.POST.get('content') is not None:
            exam.content = request.POST.get('content')
        exam.save()
        return JsonResponse({'success': True})
    except Exam.DoesNotExist:
        return JsonResponse({'error': 'Prova não encontrada'}, status=404)


@require_http_methods(["POST"])
@csrf_exempt
def api_exam_delete(request, exam_id):
    from studies.models import Exam
    try:
        Exam.objects.get(id=exam_id).delete()
        return JsonResponse({'success': True})
    except Exam.DoesNotExist:
        return JsonResponse({'error': 'Prova não encontrada'}, status=404)


# ESTUDOS - TRABALHOS CRUD
@require_http_methods(["POST"])
@csrf_exempt
def api_assignment_create(request):
    from studies.models import Assignment, Subject
    try:
        subject_id = request.POST.get('subject_id')
        due_date = request.POST.get('due_date')
        description = request.POST.get('description', '')
        
        assignment = Assignment.objects.create(
            subject_id=subject_id,
            due_date=due_date,
            description=description,
            status='pendente',
        )
        return JsonResponse({'success': True, 'assignment': {
            'id': assignment.id,
            'due_date': str(assignment.due_date),
            'status': assignment.status,
        }})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def api_assignment_edit(request, assignment_id):
    from studies.models import Assignment
    from tasks.generators import complete_auto_task
    try:
        assignment = Assignment.objects.get(id=assignment_id)
        if request.POST.get('due_date'):
            assignment.due_date = request.POST.get('due_date')
        if request.POST.get('description') is not None:
            assignment.description = request.POST.get('description')
        if request.POST.get('status'):
            assignment.status = request.POST.get('status')
            if assignment.status in ('iniciado', 'concluido', 'entregue'):
                complete_auto_task(f"assignment:{assignment.pk}:iniciar")
            if assignment.status in ('concluido', 'entregue'):
                complete_auto_task(f"assignment:{assignment.pk}:concluir")
        assignment.save()
        return JsonResponse({'success': True})
    except Assignment.DoesNotExist:
        return JsonResponse({'error': 'Trabalho não encontrado'}, status=404)


@require_http_methods(["POST"])
@csrf_exempt
def api_assignment_delete(request, assignment_id):
    from studies.models import Assignment
    try:
        Assignment.objects.get(id=assignment_id).delete()
        return JsonResponse({'success': True})
    except Assignment.DoesNotExist:
        return JsonResponse({'error': 'Trabalho não encontrado'}, status=404)


# ESTUDOS - CONTEÚDOS CRUD
@require_http_methods(["POST"])
@csrf_exempt
def api_content_create(request):
    from studies.models import StudyContent, Subject
    try:
        subject_id = request.POST.get('subject_id')
        title = request.POST.get('title')
        if not title:
            return JsonResponse({'error': 'Título obrigatório'}, status=400)
        content = StudyContent.objects.create(
            subject_id=subject_id,
            title=title,
            status='falta_estudar',
        )
        return JsonResponse({'success': True, 'content': {
            'id': content.id, 'title': content.title, 'status': content.status
        }})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def api_content_delete(request, content_id):
    from studies.models import StudyContent
    try:
        StudyContent.objects.get(id=content_id).delete()
        return JsonResponse({'success': True})
    except StudyContent.DoesNotExist:
        return JsonResponse({'error': 'Conteúdo não encontrado'}, status=404)


# ESTUDOS - NOTAS CRUD
@require_http_methods(["POST"])
@csrf_exempt
def api_grade_create(request):
    from studies.models import Grade, Subject
    try:
        grade = Grade.objects.create(
            subject_id=request.POST.get('subject_id'),
            type=request.POST.get('type', 'prova'),
            description=request.POST.get('description', ''),
            value=float(request.POST.get('value', 0)),
            bimester=int(request.POST.get('bimester', 1)),
            date=request.POST.get('date'),
        )
        return JsonResponse({'success': True, 'grade': {
            'id': grade.id, 'value': float(grade.value), 'bimester': grade.bimester
        }})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def api_grade_delete(request, grade_id):
    from studies.models import Grade
    try:
        Grade.objects.get(id=grade_id).delete()
        return JsonResponse({'success': True})
    except Grade.DoesNotExist:
        return JsonResponse({'error': 'Nota não encontrada'}, status=404)


# ESTUDOS - TEMPO
@require_http_methods(["POST"])
@csrf_exempt
def api_studylog_create(request):
    from studies.models import StudyLog, Subject
    try:
        StudyLog.objects.create(
            subject_id=request.POST.get('subject_id'),
            date=request.POST.get('date'),
            minutes=int(request.POST.get('minutes', 0)),
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

