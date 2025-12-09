from django.contrib import admin
from .models import ExpenseCategory, Expense
from core.admin import SchoolAccessMixin

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(SchoolAccessMixin, admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Expense)
class ExpenseAdmin(SchoolAccessMixin, admin.ModelAdmin):
    list_display = ('title', 'category', 'amount', 'date', 'mode')
    list_filter = ('date', 'category', 'mode')
    search_fields = ('title',)