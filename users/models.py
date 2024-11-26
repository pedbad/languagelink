from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

'''
The following code to create a custom user model that inherits from 
AbstractBaseUser and PermissionsMixin. 
This model will include an email field as the primary identifier, 
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

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email is the primary field

    def __str__(self):
        return self.email


'''
Create profile models for students and teachers. These models will store 
additional information related to each user, such as biography, languages known, 
and competency levels. We'll also set up a one-to-one relationship between the 
CustomUser model and the profile models.
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

    def __str__(self):
        return f"{self.user.email} - Teacher Profile"

    
'''
Create a Questionnaire model to store the responses from students after they register. 
This model will be linked to the StudentProfile model, and both teachers and admins 
will be able to view these responses.
'''

class Questionnaire(models.Model):
    student_profile = models.OneToOneField(StudentProfile, on_delete=models.CASCADE)
    question1 = models.TextField()  # Replace with actual questions
    question2 = models.TextField()
    # Add more fields for additional questions
    #
    completed = models.BooleanField(default=False)  # New field to track completion

    def __str__(self):
        return f"Questionnaire for {self.student_profile.user.email}"



