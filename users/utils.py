# users/utils.py
from .models import StudentProfile

def has_completed_questionnaire(user) -> bool:
  """Return True if the given user (student) has at least one completed questionnaire."""
  if getattr(user, "role", None) != "student":
    return True  # non-students aren't blocked by this rule
  try:
    sp = user.studentprofile
  except StudentProfile.DoesNotExist:
    return False
  return sp.questionnaires.filter(completed=True).exists()
