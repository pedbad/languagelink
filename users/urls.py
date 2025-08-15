# Import Django utilities
from django.urls import path
from django.contrib.auth.views import LogoutView, PasswordChangeDoneView
from django.contrib.auth import views as auth_views  # for password reset URLs


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
  toggle_can_host_online,      # Teacher availability for online meetings
  toggle_advising_status,      # Teacher availability toggle view
  delete_resource_note,        # HTMX endpoint: delete a ResourceNote
  edit_resource_note,          # HTMX endpoint: edit a ResourceNote
  view_resource_note,          # HTMX endpoint: view a ResourceNote
  NotifyingPasswordChangeView,  # add this import at the top
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
  path('teacher/toggle-online/', toggle_can_host_online, name='toggle_can_host_online'),  # route to toggle online availability
  path('teacher/toggle-advising/', toggle_advising_status, name='toggle_advising_status'),  # route to toggle teacher availability
  path('student/<int:student_id>/questionnaire/', questionnaire_view, name='student_questionnaire'),  # View student's questionnaire
  path('student/<int:student_id>/profile/', student_profile_view, name='student_profile_admin'),  # View specific student's profile
  path('student/<int:student_id>/toggle-active/', toggle_student_active, name='toggle_student_active'),
  path('student/<int:student_id>/delete/', delete_student, name='delete_student'),
  
  # Admin Dashboard
  path('admin/dashboard/', admin_dashboard_view, name='admin_dashboard'),

  # Password Management URLs
  path(
    'password-change/',
    NotifyingPasswordChangeView.as_view(template_name='users/password_change.html'),
    name='password_change'
  ),
  path(
    'password-change/done/',
    PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'),
    name='password_change_done'
  ),
  # Initiate reset (not strictly needed for invites, but useful)
  path(
    "password-reset/",
    auth_views.PasswordResetView.as_view(
      template_name="users/password_reset_form.html"
    ),
    name="password_reset",
  ),
  path(
    "password-reset/done/",
    auth_views.PasswordResetDoneView.as_view(
      template_name="users/password_reset_done.html"
    ),
    name="password_reset_done",
  ),
  path(
    "reset/<uidb64>/<token>/",
    auth_views.PasswordResetConfirmView.as_view(
      template_name="users/password_reset_confirm.html"
    ),
    name="password_reset_confirm",
  ),
  path(
    "reset/done/",
    auth_views.PasswordResetCompleteView.as_view(
      template_name="users/password_reset_complete.html"
    ),
    name="password_reset_complete",
  ),
  
  # HTMX-friendly delete endpoint for a ResourceNote
  path('notes/<int:pk>/delete/', delete_resource_note, name='delete_resource_note'),
  path('notes/<int:pk>/edit/', edit_resource_note, name='edit_resource_note'),
  path('notes/<int:pk>/view/', view_resource_note, name='view_resource_note'),
]
