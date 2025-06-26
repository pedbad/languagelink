from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, LanguageCompetency, StudentProfile, TeacherProfile, Questionnaire, ResourceNote
from django.forms import modelformset_factory, TextInput
from django.forms.widgets import ClearableFileInput
from django_ckeditor_5.widgets import CKEditor5Widget


# User Registration Form
class CustomUserCreationForm(UserCreationForm):
  # Define the role field with restricted choices
  role = forms.ChoiceField(choices=[('student', 'Student'), ('teacher', 'Teacher')], label="Role")

  class Meta(UserCreationForm.Meta):
    model = CustomUser
    fields = ('email', 'first_name', 'last_name', 'role', 'password1', 'password2')  # Only allow these fields

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Remove 'usable_password' if it exists
    self.fields.pop('usable_password', None)

  # Step 1: Add email validation logic
  def clean_email(self):
    email = self.cleaned_data.get('email')
    if CustomUser.objects.filter(email=email).exists():
      raise forms.ValidationError("This email is already in use. Please use a different email.")
    return email

  def save(self, commit=True):
    user = super().save(commit=False)
    user.role = self.cleaned_data['role']
    
    # Make sure the user is not an admin
    user.is_staff = False
    user.is_superuser = False
      
    if commit:
      user.save()
    return user


# Form for managing Language Competencies
class LanguageCompetencyForm(forms.ModelForm):
  class Meta:
    model = LanguageCompetency
    fields = ['language', 'competency_level']

# Formset for managing multiple LanguageCompetency entries
LanguageCompetencyFormSet = modelformset_factory(LanguageCompetency, form=LanguageCompetencyForm, extra=1)

# Profile Update Form for Students
class StudentProfileForm(forms.ModelForm):
  # Adding fields from the CustomUser model
  first_name = forms.CharField(max_length=30, required=True, label="First Name")
  last_name = forms.CharField(max_length=30, required=True, label="Last Name")
  email = forms.EmailField(required=True, label="Email")
  biography = forms.CharField(  # Update the biography field
    widget=forms.Textarea(attrs={'placeholder': 'Tell Us About Yourself!'}),
    required=False,  # Explicitly set as optional
    label="Language Biography",
  )
  languages_of_interest = forms.CharField(  # Add as a text area
    widget=forms.Textarea(attrs={'placeholder': 'What languages are you interested in learning?'}),
    required=False,  # Explicitly optional
    label="Languages of Interest",
  )

  class Meta:
    model = StudentProfile
    fields = ['biography', 'languages_of_interest', 'profile_picture']


  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user', None)
    super().__init__(*args, **kwargs)
    self.fields['profile_picture'].widget = ClearableFileInput(attrs={'class': 'file-input'})
    if user:
      self.fields['first_name'].initial = user.first_name
      self.fields['last_name'].initial = user.last_name
      self.fields['email'].initial = user.email
    print(type(self.fields['profile_picture'].widget))


  def save(self, commit=True):
    student_profile = super().save(commit=False)
    if commit:
      student_profile.save()
      user = student_profile.user
      user.first_name = self.cleaned_data['first_name']
      user.last_name = self.cleaned_data['last_name']
      user.email = self.cleaned_data['email']
      user.save()
    return student_profile


# Profile Update Form for Teachers
class TeacherProfileForm(forms.ModelForm):
  # Adding fields from the CustomUser model
  first_name = forms.CharField(max_length=30, required=True, label="First Name")
  last_name = forms.CharField(max_length=30, required=True, label="Last Name")
  email = forms.EmailField(required=True, label="Email")

  class Meta:
    model = TeacherProfile
    fields = ['biography', 'profile_picture', 'can_host_in_person', 'can_host_online']  # Add other fields as needed

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user', None)
    super().__init__(*args, **kwargs)
    if user:
      self.fields['first_name'].initial = user.first_name
      self.fields['last_name'].initial = user.last_name
      self.fields['email'].initial = user.email

  def save(self, commit=True):
    teacher_profile = super().save(commit=False)
    user = teacher_profile.user
    user.first_name = self.cleaned_data['first_name']
    user.last_name = self.cleaned_data['last_name']
    user.email = self.cleaned_data['email']
    if commit:
      user.save()  # Save user changes
      teacher_profile.save()  # Save profile changes
    return teacher_profile


# Questionnaire Form
# This form is used to handle the questionnaire that students fill out.
class QuestionnaireForm(forms.ModelForm):
  class Meta:
    model = Questionnaire
    fields = ['question1', 'question2']  # Add all the fields you want to include in the form
        

# ResourceNoteForm Form
# This form is used to handle the Resource Notes that teachers fill out.       
class ResourceNoteForm(forms.ModelForm):
  """
  Form for teachers to leave rich-text notes/resources for a student.
  Title gets a Tailwind-styled TextInput; content gets the CKEditor5 widget.
  """
  class Meta:
    model = ResourceNote
    fields = [
      'title',    # optional short headline
      'content',  # rich-text HTML
    ]
    widgets = {
      'title': TextInput(attrs={
        'class': 'w-full rounded border border-gray-300 p-2',
        'placeholder': 'Optional headline…',
      }),
      'content': CKEditor5Widget(config_name='default'),
    }
    labels = {
      'title':   'Title',
      'content': 'Notes & Resource Links',
    }
    help_texts = {
      'title':   'A brief title (optional).',
      'content': 'Your formatted notes, links, lists, etc.',
    }

