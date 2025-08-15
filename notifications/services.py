# notifications/services.py
# High-level notification helpers used by signal receivers.
# Keep this logic here so views/models stay clean.

# -----------------------------------------------------------------------------
# Standard library
# -----------------------------------------------------------------------------
from typing import List, TYPE_CHECKING

# -----------------------------------------------------------------------------
# Django imports
# -----------------------------------------------------------------------------
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator  # secure, time-limited tokens
from django.db import transaction
from django.urls import reverse  # build reset-confirm URL
from django.utils.encoding import force_bytes  # encode user pk
from django.utils.http import urlsafe_base64_encode  # safe uid in URLs

# -----------------------------------------------------------------------------
# Local app imports
# -----------------------------------------------------------------------------
from .email import send_plain_email

# Only for type checking (no runtime import = no circular deps)
if TYPE_CHECKING:
  from users.models import CustomUser
  from booking.models import Booking

User = get_user_model()

def admin_emails() -> List[str]:
  """
  Return a list of active admin user emails.
  Used to notify admins on certain events.
  """
  return list(
    User.objects
    .filter(is_active=True, role="admin")
    .exclude(email__isnull=True)
    .exclude(email__exact="")
    .values_list("email", flat=True)
  )

def abs_url(path: str) -> str:
  """
  Build an absolute URL for email links.
  Example: abs_url('/booking/student/bookings/')
  """
  base = getattr(settings, "SITE_URL", "http://localhost:8000").rstrip("/")
  if not path.startswith("/"):
    path = "/" + path
  return base + path

def notify_booking_created(booking):
  """
  Draft notifier for a newly created booking.
  Sends to: student (confirmation), teacher (new booking), admins (copy).
  Includes the student's message if provided.
  """
  slot = booking.teacher_availability
  teacher = slot.teacher
  student = booking.student
  when = f"{slot.date} {slot.start_time.strftime('%H:%M')}–{slot.end_time.strftime('%H:%M')}"

  # Student message (trim just in case; your model caps at ~300 chars)
  msg = (getattr(booking, "message", "") or "").strip()
  msg_for_teacher = f"\nMessage from student:\n{msg}\n" if msg else ""
  msg_for_admin = f"\nMessage:\n{msg}\n" if msg else ""
  msg_for_student = f"\nYour message to the advisor:\n{msg}\n" if msg else ""

  # Useful links (adjust to named URLs later if you prefer)
  student_link = abs_url("/booking/student/bookings/")
  teacher_link = abs_url("/booking/teacher/bookings/")
  admin_link = abs_url("/booking/admin/bookings/")

  def _send():
    # Student confirmation (echo back their message)
    send_plain_email(
      subject="Booking confirmed",
      to=[student.email],
      body_text=(
        f"Hi {getattr(student, 'first_name', '') or 'there'},\n\n"
        f"Your booking with {getattr(teacher, 'email', 'the teacher')} is confirmed.\n"
        f"When: {when}\n"
        f"{msg_for_student}"
        f"Manage your bookings: {student_link}\n"
      ),
    )

    # Teacher notification (include student's message)
    send_plain_email(
      subject="New booking received",
      to=[teacher.email],
      body_text=(
        f"Hi {getattr(teacher, 'first_name', '') or 'there'},\n\n"
        f"{getattr(student, 'email', 'A student')} booked a slot.\n"
        f"When: {when}\n"
        f"{msg_for_teacher}"
        f"Upcoming bookings: {teacher_link}\n"
      ),
    )

    # Admin copy (include message)
    admins = admin_emails()
    if admins:
      send_plain_email(
        subject="New booking (admin copy)",
        to=admins,
        body_text=(
          f"New booking created.\n"
          f"Teacher: {teacher.email}\n"
          f"Student: {student.email}\n"
          f"When: {when}\n"
          f"{msg_for_admin}"
          f"Admin bookings: {admin_link}\n"
        ),
      )

  # Ensure emails send only after DB commit
  transaction.on_commit(_send)

def notify_password_changed(user):
  """
  Security notice sent to the user after a successful password change.
  """
  name = getattr(user, "first_name", "") or "there"
  body = (
    f"Hi {name},\n\n"
    "Your LanguageLink account password was changed successfully.\n"
    "If you did not make this change, please contact an administrator immediately.\n"
  )

  # No need for on_commit here, but it's safe if the view wraps DB ops
  transaction.on_commit(lambda: send_plain_email(
    subject="Your password was changed",
    to=[user.email],
    body_text=body,
  ))

def build_set_password_url(user) -> str:
  """
  Build the password reset confirm URL for this user (time-limited).
  Django will validate the token and enforce expiry (settings.PASSWORD_RESET_TIMEOUT).
  """
  uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
  token = default_token_generator.make_token(user)
  path = reverse("password_reset_confirm", kwargs={"uidb64": uidb64, "token": token})
  return abs_url(path)

def notify_user_invited(user):
  """
  Send a role-specific invite email with a secure, time-limited link
  so the user can set their password.
  """
  link = build_set_password_url(user)
  # For info text: show timeout in hours if configured (Django default ~72h)
  try:
    hours = int(getattr(settings, "PASSWORD_RESET_TIMEOUT", 60 * 60 * 72)) // 3600
  except Exception:
    hours = 72

  name = getattr(user, "first_name", "") or "there"
  role = getattr(user, "role", "")

  if role == "student":
    after = abs_url("/users/student/questionnaire/")
    body = (
      f"Hi {name},\n\n"
      "Your LanguageLink account has been created.\n"
      f"Set your password using this secure link (expires in ~{hours} hours):\n"
      f"{link}\n\n"
      f"After setting your password, please complete the compulsory questionnaire:\n{after}\n"
    )
    subject = "Welcome to LanguageLink – Set your password"
  elif role == "teacher":
    profile_link = abs_url("/users/teacher/profile/")
    bookings_link = abs_url("/booking/teacher/bookings/")
    body = (
      f"Hi {name},\n\n"
      "Your LanguageLink advisor account has been created.\n"
      f"Set your password using this secure link (expires in ~{hours} hours):\n"
      f"{link}\n\n"
      f"Then, please review your profile and set availability:\n"
      f"- Profile: {profile_link}\n"
      f"- Bookings: {bookings_link}\n"
    )
    subject = "Welcome to LanguageLink – Set your password"
  else:
    # Fallback for admins/other roles
    body = (
      f"Hi {name},\n\n"
      "Your LanguageLink account has been created.\n"
      f"Set your password using this secure link (expires in ~{hours} hours):\n"
      f"{link}\n"
    )
    subject = "Welcome to LanguageLink – Set your password"

  transaction.on_commit(lambda: send_plain_email(
    subject=subject,
    to=[user.email],
    body_text=body,
  ))


def _admin_profile_link_for(user) -> str:
  """
  Best link for admins to jump straight to the user's profile.
  Falls back to the admin dashboard if the named URL isn't available.
  """
  try:
    role = getattr(user, "role", "")
    if role == "student":
      path = reverse("student_profile_admin", kwargs={"student_id": user.id})
      return abs_url(path)
    if role == "teacher":
      path = reverse("teacher_profile_admin", kwargs={"teacher_id": user.id})
      return abs_url(path)
  except Exception:
    # If reversing fails (e.g., URL renamed), we still give admins *somewhere* useful.
    pass
  return abs_url("/users/admin/dashboard/")

def notify_admins_user_invited(user):
  """
  Notify all admins that a new user was created and invited.
  Includes role, email, and a direct link to the user's profile page.
  """
  admins = admin_emails()
  if not admins:
    return

  role = getattr(user, "role", "(unknown)")
  email = getattr(user, "email", "(no email)")
  profile_url = _admin_profile_link_for(user)

  subject = "New user invited"
  body = (
    f"A new {role} was created and invited to set their password.\n"
    f"Email: {email}\n"
    f"Profile: {profile_url}\n"
  )

  transaction.on_commit(lambda: send_plain_email(
    subject=subject,
    to=admins,
    body_text=body,
  ))
