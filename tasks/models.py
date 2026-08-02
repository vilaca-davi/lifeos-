from django.db import models

class Task(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("concluida", "Concluída"),
    ]
    PRIORITY_CHOICES = [
        ("baixa", "Baixa"),
        ("media", "Média"),
        ("alta", "Alta"),
    ]

    title = models.CharField("Título", max_length=200)
    description = models.TextField("Descrição", blank=True)
    due_date = models.DateField("Data de vencimento", null=True, blank=True)
    status = models.CharField("Status", max_length=10, choices=STATUS_CHOICES, default="pendente")
    priority = models.CharField("Prioridade", max_length=5, choices=PRIORITY_CHOICES, default="media")
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    source_key = models.CharField(max_length=150, unique=True, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"