from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import BooleanField, Value as V, Case, When, F

from .models import CustomUser, Questionnaire, TeacherProfile, StudentProfile
from .forms import CustomUserCreationForm, TeacherProfileForm, StudentProfileForm, QuestionnaireForm


# Registration View
def register(request):
  """
  Handles user registration. Admins can register students or teachers.
  """
  if request.method == 'POST':
    form = CustomUserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()

      # Redirect based on the user's role
      if request.user.is_authenticated and request.user.role == 'admin':
        if user.role == 'student':
          return redirect('teacher_student_list')
        elif user.role == 'teacher':
          return redirect('advisors')
  else:
    form = CustomUserCreationForm()
  return render(request, 'users/register.html', {'form': form})


# Login View
def login_view(request):
  """
  Handles user login and redirection based on user roles.
  """
  if request.method == 'POST':
    email = request.POST['email']
    password = request.POST['password']
    user = authenticate(request, email=email, password=password)

    if user:
      login(request, user)

      # Session expiry logic
      if 'remember_me' in request.POST:
        request.session.set_expiry(1209600)  # 2 weeks
      else:
        request.session.set_expiry(0)  # Browser close

      # Role-based redirection
      if user.role == 'student':
        questionnaire = Questionnaire.objects.filter(student_profile__user=user).first()
        if questionnaire and not questionnaire.completed:
          return redirect('questionnaire')
        return redirect('student_profile')
      elif user.role == 'teacher':
        return redirect('teacher_profile')
      elif user.role == 'admin':
        return redirect('admin_dashboard')
    else:
      return render(request, 'users/login.html', {'error': 'Invalid credentials'})

  return render(request, 'users/login.html')


# Student Profile View
@login_required
def student_profile_view(request):
  """
  Displays and allows editing of the student's profile.
  """
  student_profile = request.user.studentprofile
  is_editing = request.GET.get('edit', False)

  if request.method == 'POST' and is_editing:
    form = StudentProfileForm(request.POST, request.FILES, instance=student_profile, user=request.user)
    if form.is_valid():
      form.save()
      return redirect('student_profile')
  else:
    form = StudentProfileForm(instance=student_profile, user=request.user)

  return render(request, 'users/student_profile.html', {
    'form': form,
    'student_profile': student_profile,
    'is_editing': is_editing,
  })


# Teacher Profile View
@login_required
def teacher_profile_view(request):
  """
  Displays and allows editing of the teacher's profile.
  """
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
  """
  Displays and handles the student questionnaire form.
  """
  student_profile = request.user.studentprofile

  # Ensure a questionnaire exists
  if not hasattr(student_profile, 'questionnaire'):
    Questionnaire.objects.create(student_profile=student_profile)

  if request.method == 'POST':
    form = QuestionnaireForm(request.POST, instance=student_profile.questionnaire)
    if form.is_valid():
      questionnaire = form.save(commit=False)
      questionnaire.completed = True
      questionnaire.save()
      return redirect('student_profile')
  else:
    form = QuestionnaireForm(instance=student_profile.questionnaire)

  return render(request, 'users/questionnaire.html', {'form': form})


# Admin Dashboard View
@login_required
def admin_dashboard_view(request):
  """
  Displays the admin dashboard.
  """
  return render(request, 'users/admin_dashboard.html')


# Student Resources View
@login_required
def student_resource_view(request):
  """
  Displays resources for students.
  """
  return render(request, 'users/student_resources.html')


# View for Listing All Teachers / Advisors
@login_required
def student_advisors_view(request):
  """
  Displays a list of all advisors (teachers).
  """
  teachers = TeacherProfile.objects.all()
  return render(request, 'users/advisors.html', {'teachers': teachers})


# View for Listing All Students
@login_required
def teacher_student_list_view(request):
  """
  Displays a list of all students, including their questionnaire completion status,
  with support for sorting by columns (First Name, Last Name, Email, etc.).
  """

  # Get sorting parameters from the query string
  sort_by = request.GET.get('sort', 'first_name')  # Default sorting column is 'first_name'
  order = request.GET.get('order', 'asc')  # Default order is ascending

  # Determine sorting direction
  order_prefix = '-' if order == 'desc' else ''  # Use '-' prefix for descending order

  # Fetch students with sorting and questionnaire status
  students = CustomUser.objects.filter(role='student').select_related('studentprofile').annotate(
    questionnaire_completed=Case(
      When(studentprofile__questionnaire__completed=True, then=V(True)),
      default=V(False),
      output_field=BooleanField(),
    )
  )

  # Apply sorting based on the selected column
  if sort_by == 'first_name':
    students = students.order_by(order_prefix + 'first_name')
  elif sort_by == 'last_name':
    students = students.order_by(order_prefix + 'last_name')
  elif sort_by == 'email':
    students = students.order_by(order_prefix + 'email')
  elif sort_by == 'questionnaire_completed':
    students = students.order_by(order_prefix + 'questionnaire_completed')

  # Pass current sorting parameters to the template for column links
  context = {
    'students': students,
    'current_sort': sort_by,
    'current_order': order,
  }

  return render(request, 'users/student_list.html', context)
