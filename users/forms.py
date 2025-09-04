"""Forms for the users app."""

# ── Third-party (Django) imports
from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.forms import modelformset_factory, TextInput
from django.forms.utils import ErrorList
from django.utils.html import format_html, format_html_join
from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _

# ── External packages
from django_ckeditor_5.widgets import CKEditor5Widget

# ── Local app imports
from .models import (
    CustomUser,
    LanguageCompetency,
    StudentProfile,
    TeacherProfile,
    Questionnaire,
    ResourceNote,
)


# ────────────────────────────────────────────────────────────────────────────────
# RegCustom error list class
# If you want to be 100% sure nothing prints when there are no errors, 
# add this small subclass and use it
# ────────────────────────────────────────────────────────────────────────────────

class TailwindErrorList(ErrorList):
    def as_ul(self):
        if not self:
            return ""
        return format_html(
            '<ul class="errorlist text-red-600 mt-1">{}</ul>',
            format_html_join("", "<li>{}</li>", ((e,) for e in self)),
        )
    
    # belt-and-suspenders: ensure string conversion never prints "[]"
    def __str__(self):
        return self.as_ul()


# ────────────────────────────────────────────────────────────────────────────────
# Registration
# ────────────────────────────────────────────────────────────────────────────────

class CustomUserCreationForm(UserCreationForm):
    """User registration with limited fields + explicit role selection."""
    role = forms.ChoiceField(
        choices=[("student", "Student"), ("teacher", "Teacher")],
        label=_("Role"),
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "first_name", "last_name", "role", "password1", "password2")

    def clean_email(self):
        """Enforce unique email (case-insensitive) at the form level."""
        email = (self.cleaned_data.get("email") or "").strip()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("This email is already in use. Please use a different email."))
        return email

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.role = self.cleaned_data["role"]
        # Ensure registrants aren't staff/superusers
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user


# ────────────────────────────────────────────────────────────────────────────────
# Language Competency
# ────────────────────────────────────────────────────────────────────────────────

class LanguageCompetencyForm(forms.ModelForm):
    class Meta:
        model = LanguageCompetency
        fields = ["language", "competency_level"]

LanguageCompetencyFormSet = modelformset_factory(
    LanguageCompetency,
    form=LanguageCompetencyForm,
    extra=1,
)


# ────────────────────────────────────────────────────────────────────────────────
# Profiles
# ────────────────────────────────────────────────────────────────────────────────

class StudentProfileForm(forms.ModelForm):
    # Fields mirrored from the related CustomUser
    first_name = forms.CharField(max_length=30, required=True, label=_("First Name"))
    last_name = forms.CharField(max_length=30, required=True, label=_("Last Name"))
    email = forms.EmailField(required=True, label=_("Email"))

    biography = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": _("Tell Us About Yourself!")}),
        required=False,
        label=_("Language Biography"),
    )
    languages_of_interest = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": _("What languages are you interested in learning?")}),
        required=False,
        label=_("Languages of Interest"),
    )

    class Meta:
        model = StudentProfile
        fields = ["biography", "languages_of_interest", "profile_picture"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["profile_picture"].widget = ClearableFileInput(attrs={"class": "file-input"})
        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email

    def save(self, commit: bool = True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            user = profile.user
            user.first_name = self.cleaned_data["first_name"]
            user.last_name = self.cleaned_data["last_name"]
            user.email = self.cleaned_data["email"]
            user.save()
        return profile


class TeacherProfileForm(forms.ModelForm):
    # Fields mirrored from the related CustomUser
    first_name = forms.CharField(max_length=30, required=True, label=_("First Name"))
    last_name = forms.CharField(max_length=30, required=True, label=_("Last Name"))
    email = forms.EmailField(required=True, label=_("Email"))

    class Meta:
        model = TeacherProfile
        fields = ["biography", "profile_picture", "can_host_in_person", "can_host_online"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email

    def save(self, commit: bool = True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            profile.save()
        return profile


# ────────────────────────────────────────────────────────────────────────────────
# Questionnaire
# ────────────────────────────────────────────────────────────────────────────────

class QuestionnaireForm(forms.ModelForm):
    LANGUAGE_GOALS_CHOICES = [
        ("personal_interest", "Personal or general interest"),
        ("fieldwork", "Fieldwork (oral communicative purposes)"),
        ("academic_reading", "Academic reading or other scholarship"),
        ("study_abroad", "Preparation for work or study abroad"),
        ("other", "Other"),
    ]

    language_mandatory_goals = forms.MultipleChoiceField(
        choices=LANGUAGE_GOALS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        initial=["other"],
    )
    language_optional_goals = forms.MultipleChoiceField(
        choices=LANGUAGE_GOALS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Questionnaire
        fields = [
            "faculty_department",
            "mother_tongue",
            "university_status",
            "language_mandatory_name",
            "language_mandatory_proficiency",
            "language_mandatory_goals",
            "language_optional_name",
            "language_optional_proficiency",
            "language_optional_goals",
            "aspects_to_improve",
            "activities_you_can_manage",
            "hours_per_week",
            "other_languages_studied",
            "additional_comments",
        ]
        widgets = {
            "university_status": forms.RadioSelect(),
            "language_mandatory_proficiency": forms.RadioSelect(),
            "language_optional_proficiency": forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the blank choice for proficiency
        self.fields["language_mandatory_proficiency"].choices = [
            c for c in self.fields["language_mandatory_proficiency"].choices if c[0] != ""
        ]
        self.fields["language_optional_proficiency"].choices = [
            c for c in self.fields["language_optional_proficiency"].choices if c[0] != ""
        ]

    def clean_language_mandatory_goals(self):
        data = self.cleaned_data.get("language_mandatory_goals")
        if not data:
            raise forms.ValidationError(_("Please select at least one learning goal."))
        return data

    def clean_other_languages_studied(self):
        data = self.cleaned_data.get("other_languages_studied")
        if not data or not data.strip():
            return "Not specified"
        return data


# ────────────────────────────────────────────────────────────────────────────────
# Resource notes
# ────────────────────────────────────────────────────────────────────────────────

class ResourceNoteForm(forms.ModelForm):
    """
    Form for teachers to leave rich-text notes/resources for a student.
    Title uses a Tailwind-styled TextInput; content uses CKEditor5.
    """
    class Meta:
        model = ResourceNote
        fields = ["title", "content"]
        widgets = {
            "title": TextInput(attrs={
                "class": "w-full rounded border border-gray-300 p-2",
                "placeholder": "Optional headline…",
            }),
            "content": CKEditor5Widget(config_name="default"),
        }
        labels = {
            "title": _("Title"),
            "content": _("Notes & Resource Links"),
        }
        help_texts = {
            "title": _("A brief title (optional)."),
            "content": _("Your formatted notes, links, lists, etc."),
        }


# ────────────────────────────────────────────────────────────────────────────────
# Password reset: styled SetPasswordForm used by PasswordResetConfirmView
# ────────────────────────────────────────────────────────────────────────────────

TAILWIND_INPUT = "w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring"

# users/forms.py
class SetPasswordFormStyled(SetPasswordForm):
    # make sure errors render as proper ErrorList (empty -> "")
    error_class = TailwindErrorList

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {TAILWIND_INPUT}".strip()
        # prevent the default HTML list from rendering under new_password1
        self.fields["new_password1"].help_text = ""
        # optional UX
        self.fields["new_password1"].widget.attrs["autocomplete"] = "new-password"
        self.fields["new_password2"].widget.attrs["autocomplete"] = "new-password"
