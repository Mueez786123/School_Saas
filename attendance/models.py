from django.db import models

# Create your models here.
from django.db import models
from core.models import School, TimeStampedModel
from academics.models import ClassGrade, Section
from students.models import Student
from accounts.models import CustomUser

class AttendanceSession(TimeStampedModel):
    """
    Yeh table record karega ki kis din, kis class ki attendance kisne li.
    (Master Table)
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='attendance_sessions')
    class_grade = models.ForeignKey(ClassGrade, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    date = models.DateField()
    taken_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        # Ek class ki ek din mein ek hi baar attendance honi chahiye
        unique_together = ('school', 'class_grade', 'section', 'date')

    def __str__(self):
        return f"{self.class_grade} - {self.section} ({self.date})"

class StudentAttendance(TimeStampedModel):
    """
    Yeh table har bacche ka status store karega (Present/Absent).
    (Detail Table)
    """
    STATUS_CHOICES = (
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Late'),
    )

    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    remarks = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ('session', 'student')

    def __str__(self):
        return f"{self.student.first_name} - {self.get_status_display()}"