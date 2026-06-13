from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path("recognize/", views.recognize_faces_view, name="recognize_faces"),
]