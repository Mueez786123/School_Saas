from django.contrib import admin
from .models import AttendanceSession, StudentAttendance
from core.admin import SchoolAccessMixin

class StudentAttendanceInline(admin.TabularInline):
    model = StudentAttendance
    extra = 0

@admin.register(AttendanceSession)
class AttendanceSessionAdmin(SchoolAccessMixin, admin.ModelAdmin):
    list_display = ('date', 'class_grade', 'section', 'taken_by')
    list_filter = ('date', 'class_grade')
    inlines = [StudentAttendanceInline]
    exclude = ('school',)