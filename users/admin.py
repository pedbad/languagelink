# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Import your models, including the new ResourceNote
from .models import (
  CustomUser,
  StudentProfile,
  TeacherProfile,
  Questionnaire,
  ResourceNote,
)


# -----------------------------------------------------------------------------
# CustomUser Admin
# -----------------------------------------------------------------------------
class CustomUserAdmin(UserAdmin):
  # Fields to display in the list view
  list_display = [
    'email', 'first_name', 'last_name',
    'role', 'is_staff', 'is_active'
  ]
  # Filters in the sidebar
  list_filter = [
    'role', 'is_staff', 'is_active'
  ]
  # Field grouping in the detail/edit view
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
  # Fields shown on the “add user” form
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

  # Remove unusable fields from the form
  def get_form(self, request, obj=None, **kwargs):
    form = super().get_form(request, obj, **kwargs)
    if 'usable_password' in form.base_fields:
      form.base_fields.pop('usable_password')
    return form


# -----------------------------------------------------------------------------
# Register models with the admin site
# -----------------------------------------------------------------------------

# Register CustomUser using the custom admin class
admin.site.register(CustomUser, CustomUserAdmin)

# Register StudentProfile with the default ModelAdmin
admin.site.register(StudentProfile)

# Register TeacherProfile with the default ModelAdmin
admin.site.register(TeacherProfile)

# Register Questionnaire with the default ModelAdmin
admin.site.register(Questionnaire)

# Register the new ResourceNote model so it appears in the admin
admin.site.register(ResourceNote)

