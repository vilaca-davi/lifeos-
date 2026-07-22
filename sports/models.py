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
    club = models.CharField("Clube", max_length=150, blank=True)
    name = models.CharField("Nome da competição", max_length=150, blank=True)

    def __str__(self):
        return f"{self.name or 'Competição'} — {self.date}"

    class Meta:
        ordering = ["-date"]
        verbose_name = "Competição"
        verbose_name_plural = "Competições"


class SwimResult(models.Model):
    EVENT_CHOICES = [
        ("50_livre", "50m Livre"),
        ("100_livre", "100m Livre"),
        ("200_livre", "200m Livre"),
        ("400_livre", "400m Livre"),
        ("50_costas", "50m Costas"),
        ("100_costas", "100m Costas"),
        ("50_peito", "50m Peito"),
        ("100_peito", "100m Peito"),
        ("50_borboleta", "50m Borboleta"),
        ("100_borboleta", "100m Borboleta"),
        ("200_medley", "200m Medley"),
        ("outro", "Outra prova"),
    ]

    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name="results", verbose_name="Competição")
    event = models.CharField("Prova", max_length=20, choices=EVENT_CHOICES)
    time_centiseconds = models.PositiveIntegerField("Tempo (centésimos)")
    placement = models.PositiveIntegerField("Colocação", null=True, blank=True)
    @property
    def formatted_time(self):
        minutes = self.time_centiseconds // 6000
        seconds = (self.time_centiseconds % 6000) // 100
        centiseconds = self.time_centiseconds % 100
        return f"{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

    def __str__(self):
        return f"{self.get_event_display()} — {self.formatted_time}"

    class Meta:
        ordering = ["event"]
        verbose_name = "Resultado"
        verbose_name_plural = "Resultados"