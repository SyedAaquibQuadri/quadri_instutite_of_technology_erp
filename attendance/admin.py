from django.contrib import admin
from .models import Attendance
# Register your models here.

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'date', 'status', 'method', 'marked_by', 'created_at']
    list_filter = ['status', 'method', 'date', 'subject__course']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'subject__name']
    date_hierarchy = 'date'
    ordering = ['-date']