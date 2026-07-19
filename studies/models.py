from django.db import models


class Subject(models.Model):
    name = models.CharField("Nome", max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Matéria"
        verbose_name_plural = "Matérias"


class Exam(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="exams", verbose_name="Matéria")
    title = models.CharField("Nome da prova", max_length=200, blank=True)
    date = models.DateField("Data")
    content = models.TextField("Conteúdo cobrado", blank=True)

    def __str__(self):
        return self.title or f"Prova de {self.subject.name} — {self.date}"

    class Meta:
        ordering = ["date"]
        verbose_name = "Prova"
        verbose_name_plural = "Provas"


class Assignment(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("iniciado", "Iniciado"),
        ("concluido", "Concluído"),
        ("entregue", "Entregue"),
    ]
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="assignments", verbose_name="Matéria")
    due_date = models.DateField("Data de entrega")
    description = models.TextField("Descrição", blank=True)
    status = models.CharField("Status", max_length=10, choices=STATUS_CHOICES, default="pendente")

    def __str__(self):
        return f"Trabalho de {self.subject.name} — {self.due_date}"

    class Meta:
        ordering = ["due_date"]
        verbose_name = "Trabalho"
        verbose_name_plural = "Trabalhos"


class StudyLog(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="study_logs", verbose_name="Matéria")
    date = models.DateField("Data")
    minutes = models.PositiveIntegerField("Minutos estudados")

    def __str__(self):
        return f"{self.subject.name} — {self.minutes} min ({self.date})"

    class Meta:
        ordering = ["-date"]
        verbose_name = "Tempo estudado"
        verbose_name_plural = "Tempos estudados"


class Grade(models.Model):
    TYPE_CHOICES = [
        ("prova", "Prova"),
        ("trabalho", "Trabalho"),
        ("atividade", "Atividade"),
        ("caderno", "Caderno"),
        ("outro", "Outro"),
    ]
    BIMESTER_CHOICES = [(1, "1º bimestre"), (2, "2º bimestre"), (3, "3º bimestre"), (4, "4º bimestre")]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="grades", verbose_name="Matéria")
    type = models.CharField("Tipo", max_length=10, choices=TYPE_CHOICES, default="prova")
    description = models.CharField("Descrição", max_length=150, blank=True)
    value = models.DecimalField("Nota", max_digits=4, decimal_places=1)
    bimester = models.PositiveSmallIntegerField("Bimestre", choices=BIMESTER_CHOICES)
    date = models.DateField("Data", null=True, blank=True)

    def __str__(self):
        return f"{self.subject.name} — {self.get_type_display()}: {self.value}"

    class Meta:
        ordering = ["bimester", "date"]
        verbose_name = "Nota"
        verbose_name_plural = "Notas"


class StudyContent(models.Model):
    STATUS_CHOICES = [
        ("falta_estudar", "Falta estudar"),
        ("estudado", "Estudado"),
        ("revisado", "Revisado"),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="contents", verbose_name="Matéria")
    title = models.CharField("Conteúdo", max_length=200)
    status = models.CharField("Status", max_length=15, choices=STATUS_CHOICES, default="falta_estudar")
    questions_done = models.BooleanField("Já coloquei as questões no Anki", default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["status", "title"]
        verbose_name = "Conteúdo estudado"
        verbose_name_plural = "Conteúdos estudados"