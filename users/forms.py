from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, LanguageCompetency, StudentProfile, TeacherProfile, Questionnaire
from django.forms import modelformset_factory
from django.forms.widgets import ClearableFileInput


# User Registration Form
class CustomUserCreationForm(UserCreationForm):
    # Define the role field with restricted choices
    role = forms.ChoiceField(choices=[('student', 'Student'), ('teacher', 'Teacher')], label="Role")
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'role')  # Only allow selection of email and role (no admin role)
    
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
    class Meta:
        model = TeacherProfile
        fields = ['biography', 'profile_picture', 'can_host_in_person', 'can_host_online']

# Questionnaire Form
# This form is used to handle the questionnaire that students fill out.
class QuestionnaireForm(forms.ModelForm):
    class Meta:
        model = Questionnaire
        fields = ['question1', 'question2']  # Add all the fields you want to include in the form
