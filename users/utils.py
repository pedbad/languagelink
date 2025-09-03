# users/utils.py
from .models import StudentProfile

def _get_student_profile(user):
    # tolerate both historical names
    return getattr(user, "student_profile", None) or getattr(user, "studentprofile", None)

def has_completed_questionnaire(user) -> bool:
    sp = _get_student_profile(user)
    if not sp:
        return False
    return sp.questionnaires.filter(completed=True).exists()

