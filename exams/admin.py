from django.contrib import admin
from .models import Exam, StudentResult
from core.admin import SchoolAccessMixin

@admin.register(Exam)
class ExamAdmin(SchoolAccessMixin, admin.ModelAdmin):
    list_display = ('name', 'start_date')
    exclude = ('school',)

@admin.register(StudentResult)
class StudentResultAdmin(SchoolAccessMixin, admin.ModelAdmin):
    list_display = ('student', 'exam', 'subject', 'marks_obtained')
    exclude = ('school',)