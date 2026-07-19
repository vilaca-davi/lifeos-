from django import forms
from .models import StudyLog

class StudyLogForm(forms.ModelForm):
    class Meta:
        model = StudyLog
        fields = ["subject", "date", "minutes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }