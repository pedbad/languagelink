from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import register, login_view, student_profile_view, student_resource_view, student_advisors_view, teacher_profile_view, questionnaire_view, admin_dashboard_view

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('student/profile/', student_profile_view, name='student_profile'),
    path('student/resource/', student_resource_view, name='student_resource'),
    path('student/advisors/', student_advisors_view, name='advisors'),
    path('teacher/profile/', teacher_profile_view, name='teacher_profile'),
    path('student/questionnaire/', questionnaire_view, name='questionnaire'),
    path('admin/dashboard/', admin_dashboard_view, name='admin_dashboard'),
]
