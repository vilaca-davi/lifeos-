from django.db import models


class CalendarEvent(models.Model):
    SOURCE_CHOICES = [
        ("manual", "Manual"),
        ("google", "Google Agenda"),
        ("auto", "Gerado automaticamente"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default="manual")
    external_id = models.CharField(max_length=255, blank=True, null=True)

    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.CharField(
        max_length=255, blank=True,
        help_text="Padrão RRULE, ex: FREQ=WEEKLY;BYDAY=TU"
    )
    show_in_upcoming = models.BooleanField(
        default=True,
        help_text="Se desmarcado, o evento aparece só no calendário, não em 'próximos eventos'"
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["start_datetime"]