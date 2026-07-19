from django import forms
from .models import StudyLog, Subject, Exam, Assignment
from .models import StudyLog, Subject, Exam, Assignment, Grade, StudyContent

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
        fields = ["subject", "title", "date", "content"]
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


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ["subject", "type", "description", "value", "bimester", "date"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }


class StudyContentForm(forms.ModelForm):
    class Meta:
        model = StudyContent
        fields = ["subject", "title", "status", "questions_done"]