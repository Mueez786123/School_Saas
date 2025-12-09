from django.db import models
from core.models import School, TimeStampedModel
from accounts.models import CustomUser

class ExpenseCategory(TimeStampedModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='expense_categories')
    name = models.CharField(max_length=100) # e.g. "Staff Salary", "Electricity"

    class Meta:
        unique_together = ('school', 'name')
        verbose_name_plural = "Expense Categories"

    def __str__(self):
        return self.name

class Expense(TimeStampedModel):
    PAYMENT_MODES = (
        ('cash', 'Cash'),
        ('online', 'Online / UPI'),
        ('cheque', 'Cheque'),
        ('transfer', 'Bank Transfer'),
    )

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=200) # e.g. "July Electricity Bill"
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    mode = models.CharField(max_length=20, choices=PAYMENT_MODES, default='cash')
    receipt = models.ImageField(upload_to='expense_receipts/', blank=True, null=True) # Proof Image
    added_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.title} - ₹{self.amount}"