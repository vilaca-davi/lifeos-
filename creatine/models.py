from django.db import models


class CreatineLog(models.Model):
    date = models.DateField("Data", unique=True)

    def __str__(self):
        return f"Creatina — {self.date}"

    class Meta:
        ordering = ["-date"]
        verbose_name = "Registro de creatina"
        verbose_name_plural = "Registros de creatina"