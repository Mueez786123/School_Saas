from django.contrib import admin

# Register your models here.
from .models import Student
from core.admin import SchoolAccessMixin
@admin.register(Student)
class StudentAdmin(SchoolAccessMixin, admin.ModelAdmin): # 👈 Mixin add kiya
    list_display = ('first_name', 'admission_no', 'current_class', 'status')
    list_filter = ('status', 'current_class') # School filter hata diya (zaroorat nahi)
    search_fields = ('first_name', 'admission_no')
    
    # School field form me chhupa do (automatic set hoga)
    exclude = ('school',)