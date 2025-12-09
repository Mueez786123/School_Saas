from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # List me role aur school dikhana zaroori hai
    list_display = ('username', 'email', 'role', 'school', 'is_staff')
    
    # Edit page pe custom fields add karne padenge
    fieldsets = UserAdmin.fieldsets + (
        ('SaaS Info', {'fields': ('role', 'school', 'phone', 'profile_picture')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('SaaS Info', {'fields': ('role', 'school', 'phone', 'profile_picture')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)