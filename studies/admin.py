from django.contrib import admin
from .models import Subject, Exam, Assignment, StudyLog, StudyFile

admin.site.register(Subject)
admin.site.register(Exam)
admin.site.register(Assignment)
admin.site.register(StudyLog)
admin.site.register(StudyFile)