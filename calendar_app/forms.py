from django import forms
from .models import CalendarEvent


class CalendarEventForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = ["title", "description", "start_datetime", "end_datetime", "is_recurring", "recurrence_rule"]
        widgets = {
            "start_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
        help_texts = {
            "recurrence_rule": "Ex: FREQ=WEEKLY;BYDAY=TU (toda terça-feira). Deixe em branco se o evento não se repete.",
        }