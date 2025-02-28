# Django Imports
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import BooleanField, Value as V, Case, When, Exists, OuterRef, Q
from django.shortcuts import render, redirect, get_object_or_404

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
      return render(request, 'users/register.html', {'form': form})
  else:
    form = CustomUserCreationForm()
  
  return render(request, 'users/register.html', {'form': form})

# Login View
def login_view(request):
  """
  Handles user login and redirects users based on their roles.
  """
  if request.method == 'POST':
    email = request.POST.get('email')
    password = request.POST.get('password')
    user = authenticate(request, email=email, password=password)

    if user:
      login(request, user)

      if 'remember_me' in request.POST:
        request.session.set_expiry(1209600)  # 2 weeks
      else:
        request.session.set_expiry(0)  # Session expires on browser close

      if user.role == 'student':
        student_profile = user.studentprofile
        has_completed_questionnaire = student_profile.questionnaires.filter(completed=True).exists()
        if not has_completed_questionnaire:
          return redirect('questionnaire')
        return redirect('student_profile')

      elif user.role == 'teacher':
        return redirect('teacher_profile')
      elif user.role == 'admin':
        return redirect('admin_dashboard')
    else:
      return render(request, 'users/login.html', {'error': 'Invalid email or password.'})

  return render(request, 'users/login.html')

# Student Profile View
@login_required
def student_profile_view(request, student_id=None):
  """
  Displays and allows editing of the student's profile.
  """
  is_admin = request.user.role == 'admin'
  is_teacher = request.user.role == 'teacher'
  is_student = request.user.role == 'student'

  # Fetch the correct student based on the user role
  if student_id and is_admin:
    student = get_object_or_404(CustomUser, id=student_id, role='student')
  elif student_id and is_teacher:
    student = get_object_or_404(CustomUser, id=student_id, role='student')
  elif is_student:
    student = request.user  # Student viewing their own profile
  else:
    raise Http404("You do not have permission to view this page.")

  # Try fetching the student's profile, handle missing profile
  try:
    student_profile = student.studentprofile
  except ObjectDoesNotExist:
    raise Http404("This student does not have a profile.")

  # Determine if editing is allowed
  is_editing = request.GET.get('edit', 'false').lower() == 'true' and (is_admin or is_student)

  if request.method == 'POST' and is_editing:
    form = StudentProfileForm(request.POST, request.FILES, instance=student_profile, user=student)
    if form.is_valid():
      form.save()
      return redirect('student_profile_admin', student_id=student.id) if is_admin else redirect('student_profile')

  else:
    form = StudentProfileForm(instance=student_profile, user=student) if is_editing else None

  return render(request, 'users/student_profile.html', {
    'student_profile': student_profile,
    'is_admin': is_admin,
    'is_teacher': is_teacher,
    'is_student': is_student,
    'is_editing': is_editing,
    'form': form,
  })


# Teacher Profile View
@login_required
def teacher_profile_view(request, teacher_id=None):
  """
  Displays and allows editing of the teacher's profile.
  - Teachers can edit their own profile.
  - Admins can view and edit any teacher's profile.
  - Students can only view advisors.
  """
  is_admin = request.user.role == 'admin'
  is_teacher = request.user.role == 'teacher'
  is_student = request.user.role == 'student'

  # If teacher_id is None, assume the logged-in teacher is accessing their own profile
  if teacher_id is None:
    if not is_teacher:
      return redirect('advisors')  # Redirect students to the advisor list
    teacher_user = request.user  # Teacher views their own profile
  else:
    teacher_user = get_object_or_404(CustomUser, id=teacher_id, role='teacher')

  # Get the teacher's profile, or return 404 if not found
  try:
    teacher_profile = teacher_user.teacherprofile
  except TeacherProfile.DoesNotExist:
    if is_admin:
      teacher_profile = None
    else:
      return render(request, "users/404.html", status=404)

  # Determine if the user is in edit mode
  is_editing = request.GET.get('edit', 'false').lower() == 'true' and (is_admin or is_teacher)

  if request.method == 'POST' and is_editing:
    form = TeacherProfileForm(request.POST, request.FILES, instance=teacher_profile, user=teacher_user)

    if form.is_valid():
      updated_profile = form.save(commit=False)

      # Handle the toggle for advising availability
      updated_profile.is_active_advisor = request.POST.get('is_active_advisor') == "on"

      updated_profile.save()
      return redirect('teacher_profile')  # Redirect to profile after saving

  else:
    form = TeacherProfileForm(instance=teacher_profile, user=teacher_user) if is_editing and teacher_profile else None

  return render(request, 'users/teacher_profile.html', {
    'teacher_profile': teacher_profile,
    'is_editing': is_editing,
    'can_edit': is_teacher or is_admin,
    'form': form,
  })
  
  
@login_required
def toggle_can_host_online(request):
  """
  Allows a teacher to toggle their availability for online hosting.
  """
  if request.user.role != 'teacher':
    return redirect('teacher_profile')  # Only teachers can perform this action

  teacher_profile = request.user.teacherprofile
  teacher_profile.can_host_online = not teacher_profile.can_host_online  # Toggle status
  teacher_profile.save()

  return redirect('teacher_profile')  # Redirect back to the profile page



# Toggle Advising Status Availability  
@login_required
def toggle_advising_status(request):
  """
  Allows a teacher to activate/deactivate themselves from advising.
  """
  if request.user.role != 'teacher':
    return redirect('teacher_profile')  # Only teachers can perform this action

  teacher_profile = request.user.teacherprofile
  teacher_profile.is_active_advisor = not teacher_profile.is_active_advisor  # Toggle status
  teacher_profile.save()

  return redirect('teacher_profile')  # Redirect back to the profile page



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



# View for Listing All Advisors
@login_required
def student_advisors_view(request):
  """
  Displays a list of all advisors (teachers) with sorting and search functionality.
  """
  # Extract sorting and search parameters
  sort = request.GET.get('sort', 'user__date_joined')  # Default sorting by user date joined
  order = request.GET.get('order', 'desc')  # Default order is descending
  search_query = request.GET.get('search', '')  # Search query

  # Determine sorting direction (prepend '-' for descending)
  if order == 'desc':
    sort = f"-{sort}"

  # Query all advisors (teachers) with optional search filter
  advisors = TeacherProfile.objects.select_related('user').filter(
    Q(user__first_name__icontains=search_query) |
    Q(user__last_name__icontains=search_query) |
    Q(user__email__icontains=search_query)
  )

  # Apply sorting safely
  valid_sort_fields = ['user__first_name', 'user__last_name', 'user__email', 'user__date_joined']
  if sort.lstrip('-') in valid_sort_fields:
    advisors = advisors.order_by(sort)
  else:
    advisors = advisors.order_by('user__date_joined')  # Fallback to default sorting

  # Pagination setup
  items_per_page = int(request.GET.get('items_per_page', 25))  # Default 25 items per page
  paginator = Paginator(advisors, items_per_page)
  page_number = request.GET.get('page', 1)
  page_obj = paginator.get_page(page_number)

  # Context for the template
  context = {
    'teachers': page_obj,  # Paginated advisors queryset
    'page_obj': page_obj,  # Page object for pagination
    'current_sort': request.GET.get('sort', 'user__date_joined'),
    'current_order': request.GET.get('order', 'desc'),
    'items_per_page': items_per_page,
    'search_query': search_query,
  }

  return render(request, 'users/advisor_list.html', context)


# View for Listing All Students
@login_required
def teacher_student_list_view(request):
  """
  Displays a list of active students with support for:
  - Sorting (first name, last name, email, date registered, questionnaire status)
  - Searching by name, email, or date registered
  - Pagination for better usability
  """
  # 1. Extract query parameters from GET request
  sort = request.GET.get('sort', 'date_joined')       # Default sort by date_joined
  order = request.GET.get('order', 'desc')            # Default descending order
  search_query = request.GET.get('search', '')        # Search query from input
  items_per_page = int(request.GET.get('items_per_page', 25))  # Default items per page
  page_number = request.GET.get('page', 1)            # Current page number

  # 2. Determine sorting direction (add '-' for descending)
  if order == 'desc':
    sort = f"-{sort}"

  # 3. Query the active students only
  students = (
    CustomUser.objects.filter(role='student', is_active=True)
    .select_related('studentprofile')  # Avoid extra queries for studentprofile
    .annotate(
      questionnaire_completed=Exists(
        Questionnaire.objects.filter(
          student_profile=OuterRef('studentprofile'),
          completed=True
        )
      )
    )
  )

  # 4. Apply search filters
  if search_query:
    students = students.filter(
      Q(first_name__icontains=search_query) |
      Q(last_name__icontains=search_query) |
      Q(email__icontains=search_query) |
      Q(date_joined__icontains=search_query)
    )

  # 5. Apply sorting
  students = students.order_by(sort)

  # 6. Paginate results
  paginator = Paginator(students, items_per_page)
  page_obj = paginator.get_page(page_number)

  # 7. Context for the template
  context = {
    'students': page_obj,                       # Paginated student queryset
    'page_obj': page_obj,                       # Page object for pagination
    'current_sort': request.GET.get('sort', 'date_joined'),
    'current_order': request.GET.get('order', 'desc'),
    'items_per_page': items_per_page,
    'search_query': search_query,
  }

  # 8. Render the template
  return render(request, 'users/student_list.html', context)


@login_required
@user_passes_test(lambda u: u.role == 'admin')  # Only allow admins to access this view
def toggle_student_active(request, student_id):
  """
  Toggles the 'is_active' status of a student.
  """
  student = get_object_or_404(CustomUser, id=student_id, role='student')
  
  # Toggle the is_active field
  student.is_active = not student.is_active
  student.save()

  # Redirect back to the student's profile page
  return redirect('student_profile_admin', student_id=student.id)


@login_required
@user_passes_test(lambda u: u.role == 'admin')  # Only allow admins to access this view
def delete_student(request, student_id):
  """
  Deletes a student from the database.
  """
  student = get_object_or_404(CustomUser, id=student_id, role='student')

  # Delete the student object
  student.delete()

  # Redirect to the student list page
  return redirect('teacher_student_list')