from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import register, login_view, student_profile_view, teacher_profile_view, questionnaire_view, admin_dashboard_view

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('student/profile/', student_profile_view, name='student_profile'),
    path('teacher/profile/', teacher_profile_view, name='teacher_profile'),
    path('student/questionnaire/', questionnaire_view, name='questionnaire'),
    path('admin/dashboard/', admin_dashboard_view, name='admin_dashboard'),
]
