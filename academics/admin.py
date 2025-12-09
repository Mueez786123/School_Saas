from django.contrib import admin
from .models import ClassGrade, Section, Subject
from core.admin import SchoolAccessMixin

@admin.register(ClassGrade)
class ClassGradeAdmin(SchoolAccessMixin, admin.ModelAdmin):
    list_display = ('name', 'created_at')
    # exclude = ('school',)  <-- YEH LINE HATA DO (Delete it)

@admin.register(Section)
class SectionAdmin(SchoolAccessMixin, admin.ModelAdmin):
    list_display = ('name', 'class_grade', 'class_teacher')
    list_filter = ('class_grade',)
    # exclude = ('school',)  <-- YEH LINE HATA DO

@admin.register(Subject)
class SubjectAdmin(SchoolAccessMixin, admin.ModelAdmin):
    list_display = ('name', 'class_grade', 'total_marks')
    list_filter = ('class_grade',)
    # exclude = ('school',)  <-- YEH LINE HATA DO