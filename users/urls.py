# users/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView, PasswordChangeDoneView

from .forms import SetPasswordFormStyled
from .views import (
    register, login_view,
    student_profile_view, student_resource_view, student_advisors_view,
    teacher_profile_view, teacher_student_list_view,
    questionnaire_view, admin_dashboard_view,
    toggle_student_active, delete_student,
    toggle_can_host_online, toggle_advising_status,
    delete_resource_note, edit_resource_note, view_resource_note,
    NotifyingPasswordChangeView,
)


# URL patterns for the app
urlpatterns = [
    # Auth
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),

    # Students
    path("student/profile/", student_profile_view, name="student_profile"),
    path("student/resource/", student_resource_view, name="student_resource"),
    path("student/questionnaire/", questionnaire_view, name="questionnaire"),
    path("student/advisors/", student_advisors_view, name="advisors"),

    # Teachers / Admin
    path("teacher/profile/", teacher_profile_view, name="teacher_profile"),
    path("teacher/<int:teacher_id>/profile/", teacher_profile_view, name="teacher_profile_admin"),
    path("teacher/students/", teacher_student_list_view, name="teacher_student_list"),
    path("teacher/toggle-online/", toggle_can_host_online, name="toggle_can_host_online"),
    path("teacher/toggle-advising/", toggle_advising_status, name="toggle_advising_status"),
    path("student/<int:student_id>/questionnaire/", questionnaire_view, name="student_questionnaire"),
    path("student/<int:student_id>/profile/", student_profile_view, name="student_profile_admin"),
    path("student/<int:student_id>/toggle-active/", toggle_student_active, name="toggle_student_active"),
    path("student/<int:student_id>/delete/", delete_student, name="delete_student"),

    path("admin/dashboard/", admin_dashboard_view, name="admin_dashboard"),

    # Password change (logged-in users)
    path(
        "password-change/",
        NotifyingPasswordChangeView.as_view(template_name="users/password_change.html"),
        name="password_change",
    ),
    path(
        "password-change/done/",
        PasswordChangeDoneView.as_view(template_name="users/password_change_done.html"),
        name="password_change_done",
    ),

    # Password reset flow (email-based)
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(template_name="users/password_reset_form.html"),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            form_class=SetPasswordFormStyled,   # ← your Tailwind-styled inputs
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
        name="password_reset_complete",
    ),

    # Resource notes (HTMX)
    path("notes/<int:pk>/delete/", delete_resource_note, name="delete_resource_note"),
    path("notes/<int:pk>/edit/", edit_resource_note, name="edit_resource_note"),
    path("notes/<int:pk>/view/", view_resource_note, name="view_resource_note"),
]
