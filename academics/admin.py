from django.contrib import admin
from .models import Department, Course, Subject


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'head_of_dept', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'duration_years', 'total_semesters']
    list_filter = ['department']
    search_fields = ['name', 'code']
    ordering = ['department', 'name']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'course', 'semester', 'credits', 'teacher']
    list_filter = ['course', 'semester']
    search_fields = ['name', 'code']
    ordering = ['course', 'semester', 'name']
    autocomplete_fields = ['teacher']