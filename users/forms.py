from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, LanguageCompetency, StudentProfile, TeacherProfile, Questionnaire
from django.forms import modelformset_factory

# User Registration Form
class CustomUserCreationForm(UserCreationForm):
    # Define the role field with restricted choices
    role = forms.ChoiceField(choices=[('student', 'Student'), ('teacher', 'Teacher')], label="Role")
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'role',)  # Only allow selection of email and role (no admin role)
    
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
    class Meta:
        model = StudentProfile
        fields = ['biography', 'languages_of_interest', 'profile_picture']

# Profile Update Form for Teachers
class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['biography', 'profile_picture', 'can_host_in_person', 'can_host_online']

# Questionnaire Form
# This form is used to handle the questionnaire that students fill out.
class QuestionnaireForm(forms.ModelForm):
    class Meta:
        model = Questionnaire
        fields = ['question1', 'question2']  # Add all the fields you want to include in the form
