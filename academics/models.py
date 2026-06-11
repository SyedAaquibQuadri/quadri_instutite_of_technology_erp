from django.db import models
from django.conf import settings


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    head_of_dept = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
        limit_choices_to={'role': 'teacher'},
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return f"{self.name} ({self.code})"


class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='courses',
    )
    duration_years = models.PositiveSmallIntegerField(default=4)
    total_semesters = models.PositiveSmallIntegerField(default=8)

    class Meta:
        ordering = ['department', 'name']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self):
        return f"{self.name} ({self.code})"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subjects',
    )
    semester = models.PositiveSmallIntegerField()
    credits = models.PositiveSmallIntegerField(default=3)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_subjects',
        limit_choices_to={'role': 'teacher'},
    )

    class Meta:
        ordering = ['course', 'semester', 'name']
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
        unique_together = [['course', 'code']]

    def __str__(self):
        return f"{self.name} ({self.code}) — Sem {self.semester}"