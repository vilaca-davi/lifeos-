from django import forms
from .models import TrainingSession, Competition


class TrainingSessionForm(forms.ModelForm):
    class Meta:
        model = TrainingSession
        fields = ["date", "status", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }


class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = ["date", "location", "result"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }