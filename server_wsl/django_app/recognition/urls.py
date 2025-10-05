from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path("upload/", views.upload_face, name='upload_face'),
    path("record/", views.record, name="student_record"),
    path("register/student/", views.register_student, name="register_student"),
    path("register/teacher/", views.register_teacher, name="register_teacher"),
    path("dashboard/student/", views.student_dashboard, name="student_dashboard"),
    path("dashboard/teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    path("teacher_view_attendance/", views.teacher_view_attendance, name="teacher_view_attendance"),
]