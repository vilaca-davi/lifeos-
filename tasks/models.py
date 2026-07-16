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

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pendente")
    priority = models.CharField(max_length=5, choices=PRIORITY_CHOICES, default="media")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title