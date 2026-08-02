from datetime import date, timedelta
from .models import Task
from studies.models import StudyContent, Exam, Assignment
from creatine.models import CreatineLog


def sync_auto_tasks():
    today = date.today()
    active_keys = set()

    # 1. Conteúdos: falta estudar
    for content in StudyContent.objects.filter(status="falta_estudar"):
        key = f"studycontent:{content.pk}:estudar"
        active_keys.add(key)
        Task.objects.update_or_create(
            source_key=key,
            defaults={
                "title": f"Estudar {content.title} de {content.subject.name}",
                "status": "pendente",
                "priority": "media",
            },
        )

    # 2. Conteúdos: estudado, falta revisar
    for content in StudyContent.objects.filter(status="estudado"):
        key = f"studycontent:{content.pk}:revisar"
        active_keys.add(key)
        Task.objects.update_or_create(
            source_key=key,
            defaults={
                "title": f"Revisar {content.title} de {content.subject.name}",
                "status": "pendente",
                "priority": "media",
            },
        )
        if not content.questions_done:
            key_anki = f"studycontent:{content.pk}:anki"
            active_keys.add(key_anki)
            Task.objects.update_or_create(
                source_key=key_anki,
                defaults={
                    "title": f"Colocar {content.title} no Anki",
                    "status": "pendente",
                    "priority": "baixa",
                },
            )

    # 3. Conteúdos: revisado, sem Anki marcado (ainda pode gerar tarefa de Anki)
    for content in StudyContent.objects.filter(status="revisado"):
        if not content.questions_done:
            key_anki = f"studycontent:{content.pk}:anki"
            active_keys.add(key_anki)
            Task.objects.update_or_create(
                source_key=key_anki,
                defaults={
                    "title": f"Colocar {content.title} no Anki",
                    "status": "pendente",
                    "priority": "baixa",
                },
            )

    # 3. Provas em até 7 dias
    horizon = today + timedelta(days=7)
    for exam in Exam.objects.filter(date__gte=today, date__lte=horizon):
        key = f"exam:{exam.pk}:estudar"
        active_keys.add(key)
        Task.objects.update_or_create(
            source_key=key,
            defaults={
                "title": f"Estudar para a prova: {exam.title or exam.subject.name}",
                "due_date": exam.date,
                "status": "pendente",
                "priority": "alta",
            },
        )

    # 4. Trabalhos: iniciar / concluir / levar na mochila
    for assignment in Assignment.objects.exclude(status="entregue"):
        subject_name = assignment.subject.name

        if assignment.status == "pendente":
            key = f"assignment:{assignment.pk}:iniciar"
            active_keys.add(key)
            Task.objects.update_or_create(
                source_key=key,
                defaults={
                    "title": f"Iniciar trabalho de {subject_name}",
                    "due_date": assignment.due_date,
                    "status": "pendente",
                    "priority": "media",
                },
            )
        elif assignment.status == "iniciado":
            key = f"assignment:{assignment.pk}:concluir"
            active_keys.add(key)
            Task.objects.update_or_create(
                source_key=key,
                defaults={
                    "title": f"Concluir trabalho de {subject_name}",
                    "due_date": assignment.due_date,
                    "status": "pendente",
                    "priority": "alta",
                },
            )

        if assignment.due_date == today + timedelta(days=1):
            key = f"assignment:{assignment.pk}:mochila"
            active_keys.add(key)
            Task.objects.update_or_create(
                source_key=key,
                defaults={
                    "title": f"Colocar trabalho de {subject_name} na mochila",
                    "due_date": today,
                    "status": "pendente",
                    "priority": "alta",
                },
            )
        
        # Se a mochila foi concluída (trabalho entregue), gera tarefa de confirmação
        if assignment.status == "entregue":
            key = f"assignment:{assignment.pk}:entregue"
            active_keys.add(key)
            Task.objects.update_or_create(
                source_key=key,
                defaults={
                    "title": f"Trabalho de {subject_name} entregue",
                    "due_date": today,
                    "status": "concluida",
                    "priority": "baixa",
                },
            )

    # 5. Creatina de hoje
    key = f"creatine:{today.isoformat()}"
    active_keys.add(key)
    already_taken = CreatineLog.objects.filter(date=today).exists()
    Task.objects.update_or_create(
        source_key=key,
        defaults={
            "title": "Tomar creatina",
            "due_date": today,
            "status": "concluida" if already_taken else "pendente",
            "priority": "baixa",
        },
    )

    # Remove tarefas automáticas cuja condição não existe mais,
    # MAS só as que ainda estão pendentes (não apaga o que você já concluiu manualmente)
    Task.objects.filter(source_key__isnull=False, status="pendente").exclude(
        source_key__in=active_keys
    ).delete()


def complete_auto_task(source_key):
    Task.objects.filter(source_key=source_key, status="pendente").update(status="concluida")
