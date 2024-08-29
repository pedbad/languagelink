from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Questionnaire
from .forms import CustomUserCreationForm, TeacherProfileForm, StudentProfileForm, QuestionnaireForm

# Registration View
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the new user to the database
            login(request, user)  # Log the user in immediately after registration

            # Redirect based on user role
            if user.role == CustomUser.Role.STUDENT:
                # No need to manually create StudentProfile; it will be created automatically by the signal
                return redirect('questionnaire')  # Redirect student to questionnaire
            elif user.role == CustomUser.Role.TEACHER:
                # Redirect teacher to their profile page
                return redirect('teacher_profile')
            else:
                # Redirect admin or any other role to a generic profile page
                return redirect('profile')
    else:
        form = CustomUserCreationForm()  # Display the empty registration form
    return render(request, 'users/register.html', {'form': form})


# Login View
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            # Check if the user is a student and has completed the questionnaire
            if user.role == 'student':
                questionnaire = Questionnaire.objects.filter(student_profile__user=user).first()
                if questionnaire and not questionnaire.completed:
                    return redirect('questionnaire')
                else:
                    return redirect('student_profile')
            elif user.role == 'teacher':
                return redirect('teacher_profile')
            elif user.role == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('home')
        else:
            return render(request, 'users/login.html', {'error': 'Invalid credentials'})
    return render(request, 'users/login.html')


# Student Profile View
@login_required
def student_profile_view(request):
    student_profile = request.user.studentprofile
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student_profile)
        if form.is_valid():
            form.save()
            return redirect('student_profile')
    else:
        form = StudentProfileForm(instance=student_profile)
    return render(request, 'users/student_profile.html', {'form': form})

# Teacher Profile View
@login_required
def teacher_profile_view(request):
    teacher_profile = request.user.teacherprofile
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, request.FILES, instance=teacher_profile)
        if form.is_valid():
            form.save()
            return redirect('teacher_profile')
    else:
        form = TeacherProfileForm(instance=teacher_profile)
    return render(request, 'users/teacher_profile.html', {'form': form})

# Questionnaire View
@login_required
def questionnaire_view(request):
    student_profile = request.user.studentprofile
    
    # Check if the questionnaire exists, and create it if it doesn't
    if not hasattr(student_profile, 'questionnaire'):
        Questionnaire.objects.create(student_profile=student_profile)
    
    if request.method == 'POST':
        form = QuestionnaireForm(request.POST, instance=student_profile.questionnaire)
        if form.is_valid():
            questionnaire = form.save(commit=False)
            questionnaire.completed = True  # Mark the questionnaire as completed
            questionnaire.save()
            return redirect('student_profile')
    else:
        form = QuestionnaireForm(instance=student_profile.questionnaire)
    
    return render(request, 'users/questionnaire.html', {'form': form})


# Admin dashboard
@login_required
def admin_dashboard_view(request):
    return render(request, 'users/admin_dashboard.html')
