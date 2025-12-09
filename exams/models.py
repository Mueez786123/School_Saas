from django.db import models
from core.models import School, TimeStampedModel
from academics.models import ClassGrade, Subject
from students.models import Student

class Exam(TimeStampedModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='exams')
    name = models.CharField(max_length=100) # e.g. "Half Yearly 2025", "Unit Test 1"
    start_date = models.DateField()
    end_date = models.DateField()
    classes = models.ManyToManyField(ClassGrade, related_name='exams') # Kaunsi classes ka exam hai
    
    def __str__(self):
        return f"{self.name} ({self.school.name})"

class StudentResult(TimeStampedModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_results')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2) # e.g. 85.50
    total_marks = models.PositiveIntegerField(default=100) # Subject se copy karenge
    
    class Meta:
        unique_together = ('exam', 'student', 'subject') # Ek exam me ek subject ke do result nahi

    def __str__(self):
        return f"{self.student.first_name} - {self.subject.name}: {self.marks_obtained}"