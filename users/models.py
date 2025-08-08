from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.timezone import now

'''
The following code creates a custom user model that inherits from 
AbstractBaseUser and PermissionsMixin. 
This model includes an email field as the primary identifier, 
along with a role field to distinguish between students, teachers, and admins.
'''

class CustomUserManager(BaseUserManager):
  def create_user(self, email, password=None, **extra_fields):
    if not email:
      raise ValueError('The Email field must be set')
    if not extra_fields.get('first_name'):
      raise ValueError('The First Name field must be set')
    if not extra_fields.get('last_name'):
      raise ValueError('The Last Name field must be set')

    email = self.normalize_email(email)
    user = self.model(email=email, **extra_fields)
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_superuser(self, email, password=None, **extra_fields):
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_superuser', True)

    if extra_fields.get('is_staff') is not True:
      raise ValueError('Superuser must have is_staff=True.')
    if extra_fields.get('is_superuser') is not True:
      raise ValueError('Superuser must have is_superuser=True.')

    return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
  ROLE_CHOICES = [
    ('student', 'Student'),
    ('teacher', 'Teacher'),
    ('admin', 'Admin'),
  ]

  email = models.EmailField(unique=True)
  role = models.CharField(max_length=20, choices=ROLE_CHOICES)
  first_name = models.CharField(max_length=30)  # Required: no blank and null
  last_name = models.CharField(max_length=30)   # Required: no blank and null
  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)  # Required for admin access
  date_joined = models.DateTimeField(default=now)  # Date user is registered

  objects = CustomUserManager()

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = []  # Email is the primary field
  
  def get_full_name(self):
      return f"{self.first_name} {self.last_name}".strip()

  def get_short_name(self):
      return self.first_name

  def __str__(self):
    return self.email


'''
Create profile models for students and teachers. These models store 
additional information related to each user, such as biography, languages known, 
and competency levels. There is a one-to-one relationship between the 
CustomUser model and these profile models.
'''

class LanguageCompetency(models.Model):
  COMPETENCY_LEVEL_CHOICES = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
  ]

  student_profile = models.ForeignKey('StudentProfile', on_delete=models.CASCADE, related_name='competencies')
  language = models.CharField(max_length=100)
  competency_level = models.CharField(max_length=20, choices=COMPETENCY_LEVEL_CHOICES)

  def __str__(self):
    return f"{self.language} - {self.competency_level}"

class StudentProfile(models.Model):
  user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  biography = models.TextField(blank=True, null=True)
  languages_of_interest = models.CharField(max_length=255, blank=True, null=True)
  profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

  def __str__(self):
    return f"{self.user.email} - Student Profile"

class TeacherProfile(models.Model):
  user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  biography = models.TextField(blank=True, null=True)
  profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
  can_host_in_person = models.BooleanField(default=False)
  can_host_online = models.BooleanField(default=False)
  bookings_link = models.URLField(max_length=250, blank=True, null=True)
  is_active_advisor = models.BooleanField(default=True)  # NEW FIELD for activation/deactivation

  def __str__(self):
    return f"{self.user.email} - {'Active' if self.is_active_advisor else 'Inactive'} Teacher Profile"


'''
The Questionnaire model stores responses from students. 
Each student can have multiple questionnaires associated with their profile, 
allowing for versioning or tracking updates over time. 
Teachers and admins can view all questionnaires for a student. 
Fields include timestamps for creation and updates, and a completion status.
'''

class Questionnaire(models.Model):
  student_profile = models.ForeignKey (
    StudentProfile,
    on_delete=models.CASCADE,
    related_name="questionnaires"  # Allows querying related questionnaires easily
  )
  
  faculty_department = models.CharField (
    max_length=150,
    blank=False,
    null=False,
    help_text="Enter your faculty or department. If none, type 'External'."
  )
  
  mother_tongue = models.CharField (
    max_length=100,
    blank=False,
    null=False,
    help_text="Enter your first/native language. If multilingual, list them separated by commas."
  ) 
  
  UNIVERSITY_STATUS_CHOICES = [
    ('undergrad_first', 'Undergraduate student (1st Year)'),
    ('undergrad_other', 'Undergraduate student (Other Years)'),
    ('mphil', 'MPhil student'),
    ('phd_first', 'PhD student (1st Year)'),
    ('phd_other', 'PhD student (Other Years)'),
    ('postdoc', 'Post-doctoral research'),
    ('academic_staff', 'Academic staff / Lecturer'),
    ('support_staff', 'Support staff'),
    ('fee_paying', 'Fee-paying member'),
    ('academic_visitor', 'Academic visitor'),
    ('other', 'Other'),
  ]

  university_status = models.CharField (
      max_length=50,
      choices=UNIVERSITY_STATUS_CHOICES,
      blank=False,
      null=False,
      default='other',
      help_text="Select your current university status."
  )
  
  # Choices for proficiency
  LANGUAGE_PROFICIENCY_CHOICES = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
  ]

  language_mandatory_name = models.CharField (
    max_length=100,
    blank=False,
    null=False,
    help_text="Specify the main language you wish to learn or improve."
  )

  language_mandatory_proficiency = models.CharField (
    max_length=20,
    choices=LANGUAGE_PROFICIENCY_CHOICES,
    blank=False,
    null=False,
  )

  language_mandatory_goals = models.JSONField (
    blank=False,
    null=False,
    help_text="List of learning/development goals selected for this language."
  )
  
  language_optional_name = models.CharField (
    max_length=100,
    blank=True,
    null=True,
    help_text="Specify an additional language you wish to learn or improve (optional)."
  )

  language_optional_proficiency = models.CharField (
    max_length=20,
    choices=LANGUAGE_PROFICIENCY_CHOICES,
    blank=True,
    null=True,
  )

  language_optional_goals = models.JSONField (
    blank=True,
    null=True,
    help_text="List of learning/development goals selected for this additional language."
  )

  aspects_to_improve = models.TextField (
    max_length=2000,
    blank=False,
    null=False,
    help_text="What specific aspects of the language(s) would you like to learn or improve?"
  )

  activities_you_can_manage = models.TextField(
    max_length=2000,
    blank=False,
    null=False,
    help_text="List the activities you can manage in the language(s)"
  )

  hours_per_week = models.CharField(
    max_length=300,
    blank=False,
    null=False,
    help_text="Roughly how many hours per week will you devote to language learning?"
  )

  other_languages_studied = models.TextField(
    max_length=1000,
    blank=True,
    null=True,
    help_text="List any other languages you have previously studied (optional)."
  )

  additional_comments = models.TextField(
    max_length=2000,
    blank=True,
    null=True,
    help_text="Any final comments you’d like to share with us (optional)."
  )

  completed = models.BooleanField(default=False)  # To track if this version was completed
  created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the questionnaire was created
  last_updated = models.DateTimeField(auto_now=True)  # Timestamp for when the questionnaire was last updated

  def __str__(self):
    return f"Questionnaire for {self.student_profile.user.email} (Created: {self.created_at})"
  
  
class ResourceNote(models.Model):
  """
  A rich-text note or resource link left by a teacher/admin for a student.

  Fields:
    student_profile: which student this note belongs to
    author:       who left it (teacher or admin)
    booking:      optional link to the specific meeting (future use)
    title:        short summary or category (future use)
    content:      HTML from CKEditor
    created_at:   when first saved
    updated_at:   when last edited
  """
  student_profile = models.ForeignKey (
    'StudentProfile',
    on_delete=models.CASCADE,
    related_name='resource_notes',
    help_text="The student who will see this note."
  )
  author = models.ForeignKey (
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True, blank=True,
    limit_choices_to=models.Q(role__in=['teacher','admin']),
    help_text="Which teacher/admin wrote this note; null if user deleted."
  )
  # FUTURE: tie note to a specific booking if desired
  booking = models.ForeignKey (
    'booking.Booking',
    on_delete=models.SET_NULL,
    null=True, blank=True,
    help_text="Optional: associate with a particular meeting."
  )
  # FUTURE: a short headline for easier listing
  title = models.CharField (
    max_length=200, blank=True,
    help_text="Optional summary (e.g. 'Pronunciation tips')."
  )
  content = models.TextField (
    help_text="Rich-text HTML (from CKEditor)."
  )
  created_at = models.DateTimeField (
    auto_now_add=True,
    help_text="When this note was first created."
  )
  updated_at = models.DateTimeField (
    auto_now=True,
    help_text="When this note was last modified."
  )

  class Meta:
    ordering = ['-updated_at', '-created_at']
    indexes = [
      models.Index(fields=['student_profile', 'created_at']),
    ]

  def __str__(self):
    """
    Display in the admin as:
      "Note for {Student Name} on YYYY-MM-DD HH:MM"
    """
    return f"Note for {self.student_profile.user.get_full_name()} on {self.created_at:%Y-%m-%d %H:%M}"


class ResourceAttachment(models.Model):
  """
  A file (image, PDF, etc.) attached to a ResourceNote.

  Fields:
    note:        which ResourceNote this belongs to
    file:        the uploaded file
    uploaded_at: when it was added
  """
  note = models.ForeignKey (
    ResourceNote,
    on_delete=models.CASCADE,
    related_name='attachments',
    help_text="The note this file augments."
  )
  file = models.FileField (
    upload_to='resource_notes/',
    help_text="Attachment to share with the student."
  )
  uploaded_at = models.DateTimeField (
    auto_now_add=True,
    help_text="When this file was uploaded."
  )

  def __str__(self):
    """
    Display the filename in the admin list.
    """
    return self.file.name
