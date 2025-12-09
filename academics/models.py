from django.db import models
from core.models import School, TimeStampedModel

class ClassGrade(TimeStampedModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=50) # e.g., "Class 10" or "Hifz-ul-Quran"
    
    class Meta:
        unique_together = ('school', 'name') # Ek school me "Class 10" do baar nahi honi chahiye
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    def __str__(self):
        return f"{self.name} - {self.school.name}"

class Section(TimeStampedModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='sections')
    class_grade = models.ForeignKey(ClassGrade, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=10) # e.g., "A", "B", "Girls Wing"
    class_teacher = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'teacher'})

    class Meta:
        unique_together = ('class_grade', 'name')

    def __str__(self):
        return f"{self.class_grade.name} - {self.name}"
    

class Subject(TimeStampedModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='subjects')
    class_grade = models.ForeignKey(ClassGrade, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=100) # e.g. "Mathematics", "English"
    total_marks = models.PositiveIntegerField(default=100) # By default 100 marks ka paper
    
    class Meta:
        unique_together = ('class_grade', 'name') # Ek class me do Maths nahi ho sakte

    def __str__(self):
        return f"{self.name} ({self.class_grade.name})"