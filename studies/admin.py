from django.contrib import admin
from .models import Subject, Exam, Assignment, StudyLog, Grade, StudyContent

admin.site.register(Subject)
admin.site.register(Exam)
admin.site.register(Assignment)
admin.site.register(StudyLog)
admin.site.register(Grade)
admin.site.register(StudyContent)