from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect

from django.db.models import BooleanField, Value as V, Case, When, F, Q

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
    questionnaire, created = Questionnaire.objects.get_or_create(student_profile=student_profile)

    # Check if the questionnaire is incomplete
    is_editing = not questionnaire.completed or request.GET.get('edit', False)

    if request.method == 'POST':
        form = QuestionnaireForm(request.POST, instance=questionnaire)
        if form.is_valid():
            questionnaire = form.save(commit=False)
            questionnaire.completed = True
            questionnaire.save()  # `last_updated` is automatically updated
            return redirect('student_profile')  # Redirect to profile after saving
    else:
        form = QuestionnaireForm(instance=questionnaire)

    return render(request, 'users/questionnaire.html', {
        'form': form,
        'is_editing': is_editing,
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
