from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('students/', views.students_list, name='students_list'),
    path('students/add/', views.student_add, name='student_add'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/deactivate/', views.student_deactivate, name='student_deactivate'),
    path('students/<int:pk>/activate/', views.student_activate, name='student_activate'),
    path('teachers/', views.teachers_list, name='teachers_list'),
    path('teachers/add/', views.teacher_add, name='teacher_add'),
    path('teachers/<int:pk>/edit/', views.teacher_edit, name='teacher_edit'),
    path('teachers/<int:pk>/deactivate/', views.teacher_deactivate, name='teacher_deactivate'),
    path('teachers/<int:pk>/activate/', views.teacher_activate, name='teacher_activate'),
    path('academics/', views.academics_overview, name='academics_overview'),
    path('academics/departments/add/', views.department_add, name='department_add'),
    path('academics/departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('academics/departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    path('academics/courses/add/', views.course_add, name='course_add'),
    path('academics/courses/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('academics/courses/<int:pk>/delete/', views.course_delete, name='course_delete'),
    path('academics/subjects/', views.subjects_list, name='subjects_list'),
    path('academics/subjects/add/', views.subject_add, name='subject_add'),
    path('academics/subjects/<int:pk>/edit/', views.subject_edit, name='subject_edit'),
    path('academics/subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
    path('students/<int:pk>/enroll-face/', views.enroll_face_view, name='enroll_face'),
    path('reports/attendance/', views.attendance_report_view, name='attendance_report'),
]