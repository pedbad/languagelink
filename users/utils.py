# users/utils.py
from django.templatetags.static import static
from .models import StudentProfile

def _get_student_profile(user):
    # tolerate both historical names
    return getattr(user, "student_profile", None) or getattr(user, "studentprofile", None)

def has_completed_questionnaire(user) -> bool:
    sp = _get_student_profile(user)
    if not sp:
        return False
    return sp.questionnaires.filter(completed=True).exists()


def absolute_avatar_url(request, user):
    """
    Return an absolute URL for the user's avatar, preferring profile.avatar_url,
    falling back to any user-level avatar_url, and then to a static default.
    """
    prof = getattr(user, "teacher_profile", None) or getattr(user, "student_profile", None)
    if prof and hasattr(prof, "avatar_url"):
        url = prof.avatar_url
    elif hasattr(user, "avatar_url"):
        url = user.avatar_url
    else:
        url = static("core/img/default-profile.png")

    if url.startswith("/"):
        url = request.build_absolute_uri(url)
    return url


