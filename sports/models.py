from django.db import models


class TrainingSession(models.Model):
    STATUS_CHOICES = [
        ("foi", "Fui"),
        ("nao_foi", "Não fui"),
        ("desculpa", "Tive uma desculpa"),
    ]
    date = models.DateField("Data", unique=True)
    status = models.CharField("Status", max_length=10, choices=STATUS_CHOICES, default="foi")
    notes = models.CharField("Observações", max_length=200, blank=True)

    def __str__(self):
        return f"{self.date} — {self.get_status_display()}"

    class Meta:
        ordering = ["-date"]
        verbose_name = "Treino"
        verbose_name_plural = "Treinos"


class Competition(models.Model):
    date = models.DateField("Data")
    location = models.CharField("Local", max_length=150, blank=True)
    result = models.CharField("Resultado", max_length=150, blank=True)

    def __str__(self):
        return f"Competição {self.date} — {self.location}"

    class Meta:
        ordering = ["-date"]
        verbose_name = "Competição"
        verbose_name_plural = "Competições"