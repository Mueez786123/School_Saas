from django.contrib import admin
from .models import FeeCategory, FeeStructure, FeePayment
from core.admin import SchoolAccessMixin

@admin.register(FeeCategory)
class FeeCategoryAdmin(SchoolAccessMixin, admin.ModelAdmin):
    list_display = ('name',)
    exclude = ('school',)

@admin.register(FeeStructure)
class FeeStructureAdmin(SchoolAccessMixin, admin.ModelAdmin):
    list_display = ('class_grade', 'category', 'amount')
    list_filter = ('class_grade',)
    exclude = ('school',)

@admin.register(FeePayment)
class FeePaymentAdmin(SchoolAccessMixin, admin.ModelAdmin):
    list_display = ('student', 'amount_paid', 'payment_date', 'mode')
    list_filter = ('payment_date', 'mode')
    exclude = ('school',)   