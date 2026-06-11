from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, StudentProfile, TeacherProfile


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'Student Profile'
    fk_name = 'user'
    extra = 0


class TeacherProfileInline(admin.StackedInline):
    model = TeacherProfile
    can_delete = False
    verbose_name_plural = 'Teacher Profile'
    fk_name = 'user'
    extra = 0


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'get_full_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']

    fieldsets = UserAdmin.fieldsets + (
        ('ERP Info', {'fields': ('role', 'profile_pic', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('ERP Info', {'fields': ('role', 'profile_pic', 'phone')}),
    )

    def get_inlines(self, request, obj=None):
        if obj is None:
            return []
        if obj.role == 'student':
            return [StudentProfileInline]
        if obj.role == 'teacher':
            return [TeacherProfileInline]
        return []


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['roll_no', 'user', 'course', 'current_semester', 'batch_year']
    list_filter = ['course', 'current_semester', 'batch_year']
    search_fields = ['roll_no', 'user__username', 'user__first_name', 'user__last_name']
    ordering = ['roll_no']


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'department', 'designation', 'joining_date']
    list_filter = ['department']
    search_fields = ['employee_id', 'user__username', 'user__first_name', 'user__last_name']
    ordering = ['employee_id']