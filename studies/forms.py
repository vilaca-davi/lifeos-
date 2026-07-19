from django import forms
from .models import StudyLog, Subject, Exam, Assignment, StudyFile


class StudyLogForm(forms.ModelForm):
    class Meta:
        model = StudyLog
        fields = ["subject", "date", "minutes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["name"]


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ["subject", "date", "content", "grade"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["subject", "due_date", "description", "status"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }


class StudyFileForm(forms.ModelForm):
    class Meta:
        model = StudyFile
        fields = ["subject", "title", "file"]