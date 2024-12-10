# Django Imports
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import BooleanField, Value as V, Case, When, Exists, OuterRef, Q

# App Imports
from .models import CustomUser, Questionnaire, TeacherProfile, StudentProfile
from .forms import (
  CustomUserCreationForm,
  TeacherProfileForm,
  StudentProfileForm,
  QuestionnaireForm
)

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
  Handles user login and redirects users based on their roles:
  - Students are redirected to the questionnaire page if they have no completed questionnaires.
  - Teachers are redirected to their profile page.
  - Admins are redirected to the admin dashboard.
  """
  if request.method == 'POST':
    # Retrieve email and password from the POST request
    email = request.POST.get('email')
    password = request.POST.get('password')

    # Authenticate the user
    user = authenticate(request, email=email, password=password)

    if user:
      # Log in the user
      login(request, user)

      # Session expiry logic: 'remember_me' sets a 2-week expiry, otherwise session expires on browser close
      if 'remember_me' in request.POST:
        request.session.set_expiry(1209600)  # 2 weeks
      else:
        request.session.set_expiry(0)  # Session expires when the browser is closed

      # Role-based redirection
      if user.role == 'student':
        # Retrieve the student's profile and check for completed questionnaires
        student_profile = user.studentprofile
        has_completed_questionnaire = student_profile.questionnaires.filter(completed=True).exists()

        # Redirect to questionnaire page in edit mode if no completed questionnaire exists
        if not has_completed_questionnaire:
          return redirect('questionnaire')  # Student must fill out the questionnaire

        # If a completed questionnaire exists, redirect to the student profile page
        return redirect('student_profile')

      elif user.role == 'teacher':
        # Redirect teachers to their profile page
        return redirect('teacher_profile')

      elif user.role == 'admin':
        # Redirect admins to the admin dashboard
        return redirect('admin_dashboard')

    else:
      # Render login page with an error message for invalid credentials
      return render(request, 'users/login.html', {'error': 'Invalid email or password.'})

  # Render the login page for GET requests or failed login attempts
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
def questionnaire_view(request, student_id=None):
  """
  Handles the questionnaire view for both students and admins.

  - Students: Can view and edit their own questionnaire.
  - Admins: Can view a student's completed questionnaire in read-only mode.
  """
  if student_id:
    # Admin is viewing a specific student's questionnaire
    student = CustomUser.objects.filter(id=student_id, role='student').first()
    if not student or not hasattr(student, 'studentprofile'):
      return render(request, '404.html', status=404)  # Render a 404 page if the student does not exist
    student_profile = student.studentprofile
    is_editing = False  # Admins cannot edit student questionnaires
  else:
    # Student is viewing their own questionnaire
    student = request.user
    student_profile = request.user.studentprofile

    # Check if the student has any completed questionnaires
    has_completed_questionnaires = student_profile.questionnaires.filter(completed=True).exists()

    # Determine if the user is in edit mode
    is_editing = request.GET.get('edit', 'false').lower() == 'true'
    if not has_completed_questionnaires:
      is_editing = True  # Force edit mode if no completed questionnaires exist

  # Get the latest questionnaire for display
  latest_questionnaire = student_profile.questionnaires.order_by('-created_at').first()

  if request.method == 'POST' and is_editing:
    # Handle form submission for editing or creating a questionnaire
    form = QuestionnaireForm(request.POST)
    if form.is_valid():
      new_questionnaire = form.save(commit=False)
      new_questionnaire.student_profile = student_profile  # Associate the questionnaire with the student profile
      new_questionnaire.completed = True  # Mark the questionnaire as completed
      new_questionnaire.save()
      return redirect('questionnaire')  # Redirect to prevent duplicate submissions
  else:
    # Pre-fill the form with the latest questionnaire data if available
    form = QuestionnaireForm(instance=latest_questionnaire)

  return render(request, 'users/questionnaire.html', {
    'form': form,  # Form for editing or displaying the questionnaire
    'is_editing': is_editing,  # Whether the user is in edit mode
    'student': student,  # Student object for displaying name in the template
    'latest_questionnaire': latest_questionnaire,  # Latest questionnaire for context
    'questionnaires': student_profile.questionnaires.filter(completed=True).order_by('-created_at'),  # Completed questionnaires
  })


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
  Displays a list of all students, with support for searching, sorting, and pagination.
  """
  # Get sorting parameters
  sort = request.GET.get('sort', 'date_joined')  # Default sort is by date_joined
  order = request.GET.get('order', 'desc')  # Default order is descending
  search_query = request.GET.get('search', '')  # Search query from the search box
  items_per_page = request.GET.get('items_per_page', 25)  # Default to 25 items per page

  # Determine sorting direction
  if order == 'desc':
    sort = f"-{sort}"

  # Annotate students with the questionnaire completion status
  students = (
    CustomUser.objects.filter(role='student')
    .select_related('studentprofile')
    .annotate(
      questionnaire_completed=Exists(
        Questionnaire.objects.filter(
          student_profile=OuterRef('studentprofile'),
          completed=True
        )
      )
    )
  )

  # Apply search filters
  if search_query:
    students = students.filter(
      Q(first_name__icontains=search_query)
      | Q(last_name__icontains=search_query)
      | Q(email__icontains=search_query)
      | Q(date_joined__icontains=search_query)
    )

  # Apply sorting
  students = students.order_by(sort)

  # Paginate results
  paginator = Paginator(students, items_per_page)
  page_number = request.GET.get('page', 1)
  page_obj = paginator.get_page(page_number)

  # Pass context to template
  context = {
    'students': page_obj,
    'page_obj': page_obj,
    'current_sort': request.GET.get('sort', 'date_joined'),  # Default to 'date_joined'
    'current_order': request.GET.get('order', 'desc'),  # Default to 'desc'
    'items_per_page': int(items_per_page),
    'search_query': search_query,
  }
  return render(request, 'users/student_list.html', context)

  """
  Displays a list of all students, with support for searching, sorting, and pagination.
  """
  # Get sorting parameters
  sort = request.GET.get('sort', 'date_joined')  # Default sort is by date_joined
  order = request.GET.get('order', 'desc')  # Default order is descending
  search_query = request.GET.get('search', '')  # Search query from the search box
  items_per_page = request.GET.get('items_per_page', 25)  # Default to 25 items per page

  # Determine sorting direction
  if order == 'desc':
    sort = f"-{sort}"

  # Fetch students with sorting and search functionality
  students = CustomUser.objects.filter(role='student').select_related('studentprofile').annotate(
    questionnaire_completed=Case(
      When(studentprofile__questionnaire__completed=True, then=V(True)),
      default=V(False),
      output_field=BooleanField(),
    )
  )

  # Apply search filters
  if search_query:
    students = students.filter(
      Q(first_name__icontains=search_query) |
      Q(last_name__icontains=search_query) |
      Q(email__icontains=search_query) |
      Q(date_joined__icontains=search_query)
    )

  # Apply sorting
  students = students.order_by(sort)

  # Paginate results
  paginator = Paginator(students, items_per_page)
  page_number = request.GET.get('page', 1)
  page_obj = paginator.get_page(page_number)

  # Pass context to template
  context = {
    'students': page_obj,
    'page_obj': page_obj,
    'current_sort': request.GET.get('sort', 'date_joined'),  # Default to 'date_joined'
    'current_order': request.GET.get('order', 'desc'),  # Default to 'desc'
    'items_per_page': int(items_per_page),
    'search_query': search_query,
  }
  return render(request, 'users/student_list.html', context)