from django.db import models
from django.conf import settings
from academics.models import Subject

# Create your models here.
class Attendance(models.Model):
    STATUS_CHOICES = [
    ('Present', 'Present'),
    ('Absent', 'Absent'),
    ('Late', 'Late'),
    ]

    METHOD_CHOICES = [
        ('manual', 'Manual'),
        ('face', 'Face Recognition'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        limit_choices_to={'role': 'student'},
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='attendance_records',
    )
    date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Absent',
    )
    method = models.CharField(
        max_length=10,
        choices=METHOD_CHOICES,
        default='manual',
    )
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='attendance_marked',
        limit_choices_to={'role__in': ['admin', 'teacher']},
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'subject', 'date')
        ordering = ['-date', 'subject', 'student']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.subject.name} - {self.date} - {self.status}"