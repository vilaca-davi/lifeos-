from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Exam(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="exams")
    date = models.DateField()
    content = models.TextField(blank=True, verbose_name="Conteúdo cobrado")
    grade = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    def __str__(self):
        return f"Prova de {self.subject.name} — {self.date}"

    class Meta:
        ordering = ["date"]


class Assignment(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("iniciado", "Iniciado"),
        ("concluido", "Concluído"),
        ("entregue", "Entregue"),
    ]
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="assignments")
    due_date = models.DateField()
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pendente")

    def __str__(self):
        return f"Trabalho de {self.subject.name} — {self.due_date}"

    class Meta:
        ordering = ["due_date"]


class StudyLog(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="study_logs")
    date = models.DateField()
    minutes = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.subject.name} — {self.minutes} min ({self.date})"

    class Meta:
        ordering = ["-date"]


class StudyFile(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="files")
    title = models.CharField(max_length=150)
    file = models.FileField(upload_to="studies/")

    def __str__(self):
        return self.title