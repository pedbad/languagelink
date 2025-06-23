# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Import your models
from .models import (
  CustomUser,
  StudentProfile,
  TeacherProfile,
  Questionnaire,
  ResourceNote,
  ResourceAttachment,
)


# -----------------------------------------------------------------------------
# CustomUser Admin
# -----------------------------------------------------------------------------
class CustomUserAdmin(UserAdmin):
  """
  Admin display & forms for CustomUser.
  Excludes the 'usable_password' field from forms.
  """
  list_display = [
    'email', 'first_name', 'last_name',
    'role', 'is_staff', 'is_active'
  ]
  list_filter = [
    'role', 'is_staff', 'is_active'
  ]
  fieldsets = (
    (None, {
      'fields': ('email', 'password')
    }),
    ('Personal Info', {
      'fields': ('first_name', 'last_name')
    }),
    ('Permissions', {
      'fields': ('is_staff', 'is_active', 'is_superuser')
    }),
    ('Role', {
      'fields': ('role',)
    }),
  )
  add_fieldsets = (
    (None, {
      'classes': ('wide',),
      'fields': (
        'email', 'password1', 'password2',
        'first_name', 'last_name',
        'role', 'is_staff', 'is_active'
      )
    }),
  )
  search_fields = ('email', 'first_name', 'last_name')
  ordering = ('email',)

  def get_form(self, request, obj=None, **kwargs):
    """
    Remove 'usable_password' from the form if present.
    """
    form = super().get_form(request, obj, **kwargs)
    if 'usable_password' in form.base_fields:
      form.base_fields.pop('usable_password')
    return form


# -----------------------------------------------------------------------------
# Register models with the admin site
# -----------------------------------------------------------------------------
admin.site.register(CustomUser, CustomUserAdmin)  # Register CustomUser
admin.site.register(StudentProfile)               # Student profiles
admin.site.register(TeacherProfile)               # Teacher profiles
admin.site.register(Questionnaire)                # Questionnaires

# ResourceNotes: rich-text notes / links for students
admin.site.register(ResourceNote)

# ResourceAttachments: optional file uploads for each note
admin.site.register(ResourceAttachment)
