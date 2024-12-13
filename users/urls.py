# Import Django utilities
from django.urls import path
from django.contrib.auth.views import LogoutView, PasswordChangeView, PasswordChangeDoneView

# Import app views
from .views import (
  register,                    # Handles user registration
  login_view,                  # Handles user login
  student_profile_view,        # Displays/edit student profile
  student_resource_view,       # Displays resources for students
  student_advisors_view,       # Displays advisors/teachers
  teacher_profile_view,        # Displays/edit teacher profile
  teacher_student_list_view,   # Displays list of students for teachers/admins
  questionnaire_view,          # Handles student/admin questionnaires
  admin_dashboard_view,        # Displays admin dashboard
  toggle_student_active,       # Import the new toggle active view
  delete_student,              # Placeholder for the delete functionality
)

# URL patterns for the app
urlpatterns = [
  # Authentication URLs
  path('register/', register, name='register'),
  path('login/', login_view, name='login'),
  path('logout/', LogoutView.as_view(next_page='/'), name='logout'),

  # Student URLs
  path('student/profile/', student_profile_view, name='student_profile'),
  path('student/resource/', student_resource_view, name='student_resource'),
  path('student/questionnaire/', questionnaire_view, name='questionnaire'),  # Student's own questionnaire
  path('student/advisors/', student_advisors_view, name='advisors'),  # View for listing all advisors/teachers

  # Admin/Teacher URLs
  path('teacher/profile/', teacher_profile_view, name='teacher_profile'),
  path('teacher/<int:teacher_id>/profile/', teacher_profile_view, name='teacher_profile_admin'),
  path('teacher/students/', teacher_student_list_view, name='teacher_student_list'),
  path('student/<int:student_id>/questionnaire/', questionnaire_view, name='student_questionnaire'),  # View student's questionnaire
  path('student/<int:student_id>/profile/', student_profile_view, name='student_profile_admin'),  # View specific student's profile
  path('student/<int:student_id>/toggle-active/', toggle_student_active, name='toggle_student_active'),
  path('student/<int:student_id>/delete/', delete_student, name='delete_student'),

  # Admin Dashboard
  path('admin/dashboard/', admin_dashboard_view, name='admin_dashboard'),

  # Password Management URLs
  path('password-change/', PasswordChangeView.as_view(template_name='users/password_change.html'), name='password_change'),
  path('password-change/done/', PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), name='password_change_done'),
]
