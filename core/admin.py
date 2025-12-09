from django.contrib import admin
from .models import School

class SchoolAccessMixin:
    """
    1. Superuser: Sab kuch dekh/edit kar sakta hai.
    2. School Admin: Sirf apna data dekh sakta hai.
    """
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(school=request.user.school)

    def save_model(self, request, obj, form, change):
        # Sirf Non-Superuser ke liye automatic school set karo
        if not request.user.is_superuser:
            obj.school = request.user.school
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if hasattr(db_field.related_model, 'school'):
                kwargs["queryset"] = db_field.related_model.objects.filter(school=request.user.school)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # 👇 YEH NAYA METHOD ADD KARO (Dynamic Hiding)
    def get_exclude(self, request, obj=None):
        # Agar Superuser nahi hai, toh 'school' field chhupa do
        if not request.user.is_superuser:
            return ('school',)
        # Agar Superuser hai, toh kuch mat chhupao
        return []

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'subscription_end_date')