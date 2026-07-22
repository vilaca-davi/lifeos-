import re
from django import forms
from .models import TrainingSession, Competition, SwimResult


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
        fields = ["date", "club", "name"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }


TIME_PATTERN = re.compile(r"^(\d{1,2}):(\d{2})\.(\d{2})$")


class SwimResultForm(forms.ModelForm):
    time = forms.CharField(
        label="Tempo",
        widget=forms.TextInput(attrs={"placeholder": "00:32.15"}),
        help_text="Formato: minutos:segundos.centésimos, ex: 00:32.15",
    )

    class Meta:
        model = SwimResult
        fields = ["competition", "event", "time", "placement"]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["time"].initial = self.instance.formatted_time

    def clean_time(self):
        value = self.cleaned_data["time"]
        match = TIME_PATTERN.match(value.strip())
        if not match:
            raise forms.ValidationError("Use o formato MM:SS.CC, ex: 00:32.15")
        minutes, seconds, centiseconds = match.groups()
        if int(seconds) >= 60:
            raise forms.ValidationError("Segundos devem ser menores que 60.")
        total = int(minutes) * 6000 + int(seconds) * 100 + int(centiseconds)
        return total

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.time_centiseconds = self.cleaned_data["time"]
        if commit:
            instance.save()
        return instance