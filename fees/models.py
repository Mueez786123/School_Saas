from django.db import models
from core.models import School, TimeStampedModel
from academics.models import ClassGrade
from students.models import Student

# 1. Fees ke prakaar (Tuition, Exam, Sports, etc.)
class FeeCategory(TimeStampedModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='fee_categories')
    name = models.CharField(max_length=100) # e.g. "Monthly Tuition", "Annual Function"
    
    class Meta:
        unique_together = ('school', 'name')
        verbose_name_plural = "Fee Categories"

    def __str__(self):
        return f"{self.name} ({self.school.name})"

# 2. Kis Class ki kitni fees hai? (Rate Card)
class FeeStructure(TimeStampedModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='fee_structures')
    class_grade = models.ForeignKey(ClassGrade, on_delete=models.CASCADE, related_name='fee_structures')
    category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2) # e.g. 1500.00
    
    class Meta:
        unique_together = ('class_grade', 'category') # Ek class me 'Tuition Fee' ki do entries nahi ho sakti

    def __str__(self):
        return f"{self.class_grade.name} - {self.category.name}: ₹{self.amount}"

# 3. Paise lene ka record (Transaction)
class FeePayment(TimeStampedModel):
    PAYMENT_MODES = (
        ('cash', 'Cash'),
        ('online', 'Online / UPI'),
        ('cheque', 'Cheque'),
    )

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='payments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    mode = models.CharField(max_length=20, choices=PAYMENT_MODES, default='cash')
    remarks = models.TextField(blank=True, help_text="Optional: Receipt no or transaction ID")

    def __str__(self):
        return f"{self.student.first_name} - ₹{self.amount_paid}"