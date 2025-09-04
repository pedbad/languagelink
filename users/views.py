# -----------------------------------------------------------------------------
# Standard library
# -----------------------------------------------------------------------------
import re
from datetime import datetime

# -----------------------------------------------------------------------------
# Django imports
# -----------------------------------------------------------------------------
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import PasswordChangeView  # subclassed below
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef, Q
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_http_methods

# -----------------------------------------------------------------------------
# Local application imports
# -----------------------------------------------------------------------------
from users.utils import has_completed_questionnaire
from .forms import (
  CustomUserCreationForm,
  QuestionnaireForm,
  ResourceNoteForm,
  StudentProfileForm,
  TeacherProfileForm,
)
from .models import (
  CustomUser,
  Questionnaire,
  ResourceNote,
  TeacherProfile,
)

# -----------------------------------------------------------------------------
# Notifications (local app)
# -----------------------------------------------------------------------------
# Notifications (local app)
from notifications.services import (
  notify_password_changed,
  notify_user_invited,
  notify_admins_user_invited,
  notify_resource_note_created,
)



# Registration View
@login_required
@user_passes_test(lambda u: u.role in ('admin', 'teacher'))
def register(request):
  """
  Create a new user (student or teacher), send a secure invite email,
  and ALWAYS redirect after a successful POST to avoid resubmits.
  """
  if request.method == 'POST':
    form = CustomUserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()

      # Force the new user to set their own password via email link
      user.set_unusable_password()
      user.save(update_fields=['password'])

      # Notify: invite the user + inform admins
      notify_user_invited(user)
      notify_admins_user_invited(user)

      # Choose a sensible redirect based on the *created* user's role
      # (adjust targets if you prefer different destinations)
      if user.role == 'student':
        return redirect('teacher_student_list')   # e.g., the list teachers/admins manage
      elif user.role == 'teacher':
        return redirect('advisors')               # or a staff list page if you have one
      else:
        return redirect('admin_dashboard')        # fallback

    # Invalid form → re-render with errors
    return render(request, 'users/register.html', {'form': form}, status=400)

  # GET: show blank form (optionally prefill role from querystring)
  form = CustomUserCreationForm()  # or CustomUserCreationForm(initial={'role': request.GET.get('role')})
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
        student_profile = getattr(user, "student_profile", None)
        completed = student_profile and student_profile.questionnaires.filter(completed=True).exists()
        if not completed:
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
def student_profile_view(request, student_id = None):
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
    student_profile = student.student_profile
  except ObjectDoesNotExist:
    raise Http404("This student does not have a profile.")

  # Check if questionnaire is completed
  has_completed_questionnaire = student_profile.questionnaires.filter(completed=True).exists()


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
    'has_completed_questionnaire': has_completed_questionnaire,
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
  is_admin   = request.user.role == 'admin'
  is_teacher = request.user.role == 'teacher'
  is_student = request.user.role == 'student'

  # Whose profile are we looking at?
  if teacher_id is None:
      # Only teachers (their own page) or admins should reach here; others go to advisors
      if not (is_teacher or is_admin):
          return redirect('advisors')
      # If admin hits the self URL with no id, you can choose to redirect them elsewhere
      if is_teacher:
          teacher_user = request.user
      else:
          return redirect('advisors')  # or wherever your admin starts from
  else:
      teacher_user = get_object_or_404(CustomUser, id=teacher_id, role='teacher')

  # Edit permissions
  can_edit_self = (is_teacher and request.user.id == teacher_user.id)

  # IMPORTANT: For POST, don't rely on ?edit=true (which won't be present).
  if request.method == 'POST':
      is_editing = (is_admin or can_edit_self)
  else:
      wants_edit = request.GET.get('edit', 'false').lower() == 'true'
      is_editing = wants_edit and (is_admin or can_edit_self)

  # Fetch profile without 404
  try:
      teacher_profile = teacher_user.teacher_profile
  except TeacherProfile.DoesNotExist:
      teacher_profile = None

  # If editing, ensure there's a profile instance to bind the form to
  if is_editing and teacher_profile is None:
      teacher_profile, _ = TeacherProfile.objects.get_or_create(user=teacher_user)

  # Form handling
  if request.method == 'POST' and is_editing:
      form = TeacherProfileForm(
          request.POST, request.FILES,
          instance=teacher_profile,
          user=teacher_user
      )
      if form.is_valid():
          updated_profile = form.save()

          # If is_active_advisor is NOT a form field, keep the toggle; otherwise remove these two lines.
          updated_profile.is_active_advisor = (request.POST.get('is_active_advisor') == 'on')
          updated_profile.save()

          # Redirect appropriately
          if teacher_id is not None:
              return redirect('teacher_profile_admin', teacher_id=teacher_user.id)  # <- adjust to your URL name
          return redirect('teacher_profile')
  else:
      form = TeacherProfileForm(instance=teacher_profile, user=teacher_user) if is_editing else None

  # Student booking gate
  can_student_book = has_completed_questionnaire(request.user) if is_student else True

  return render(request, 'users/teacher_profile.html', {
      'teacher_profile': teacher_profile,
      'teacher_user': teacher_user,
      'is_editing': is_editing,
      'can_edit': (is_admin or can_edit_self),
      'form': form,
      'can_student_book': can_student_book,
      'is_student': is_student,
  })

  
  
@login_required
def toggle_can_host_in_person(request):
  """
  Allows a teacher to toggle their availability for in-person hosting.
  """
  if request.user.role != 'teacher':
    return redirect('teacher_profile')  # Only teachers can perform this action

  teacher_profile, _ = TeacherProfile.objects.get_or_create(user=request.user)
  teacher_profile.can_host_in_person = not teacher_profile.can_host_in_person  # Toggle status
  teacher_profile.save()

  return redirect('teacher_profile')  # Redirect back to the profile page

  
@login_required
def toggle_can_host_online(request):
  """
  Allows a teacher to toggle their availability for online hosting.
  """
  if request.user.role != 'teacher':
    return redirect('teacher_profile')  # Only teachers can perform this action

  teacher_profile, _ = TeacherProfile.objects.get_or_create(user=request.user)
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

  teacher_profile, _ = TeacherProfile.objects.get_or_create(user=request.user)
  teacher_profile.is_active_advisor = not teacher_profile.is_active_advisor  # Toggle status
  teacher_profile.save()

  return redirect('teacher_profile')  # Redirect back to the profile page


# Questionnaire View
@login_required
def questionnaire_view(request, student_id=None):
  """
  Students: view/edit own questionnaire
  Teachers/Admins: view a student's questionnaire (read-only)
  """
  # Determine whose questionnaire is being viewed
  if student_id is not None:
    # 🔒 only staff (teacher/admin) can view another student's page
    if request.user.role not in ('teacher', 'admin'):
      return HttpResponseForbidden("Not allowed")

    student = get_object_or_404(CustomUser, id=student_id, role='student')
    student_profile = getattr(student, 'student_profile', None)
    if not student_profile:
      return render(request, '404.html', status=404)

    is_owner = False
    is_editing = False  # staff cannot edit
  else:
    # Student viewing their own
    student = request.user
    student_profile = student.student_profile
    is_owner = True
    is_editing = request.GET.get('edit', 'false').lower() == 'true'

  # ✅ unified completed flag (singular)
  has_completed = student_profile.questionnaires.filter(completed=True).exists()

  # Force edit if owner has never completed
  if is_owner and not has_completed:
    is_editing = True

  latest_questionnaire = student_profile.questionnaires.order_by('-created_at').first()

  if request.method == 'POST' and is_owner and is_editing:
    form = QuestionnaireForm(request.POST)
    if form.is_valid():
      obj = form.save(commit=False)
      obj.student_profile = student_profile
      obj.completed = True
      obj.save()
      # Student just submitted their own form
      return redirect('questionnaire')
  else:
    form = QuestionnaireForm(instance=latest_questionnaire)

  return render(request, 'users/questionnaire.html', {
    'form': form,
    'is_editing': is_editing,
    'student': student,
    'latest_questionnaire': latest_questionnaire,
    'questionnaires': student_profile.questionnaires.filter(completed=True).order_by('-created_at'),
    'has_completed_questionnaire': has_completed, 
    'is_owner': is_owner,
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
  Displays resources (notes) for a given student.
  - Students see their own notes.
  - Teachers/Admins may view any student by passing ?student_id=<id>.
  - Only *teachers* get an Add-Note form.
  """
  user = request.user

  # 1) Determine which student’s page we’re on
  if user.role in ('teacher', 'admin'):
    sid = request.GET.get('student_id')
    if not sid:
      # No student_id → bounce back
      return redirect('teacher_student_list') if user.role == 'teacher' else redirect('admin_dashboard')
    student_user = get_object_or_404(CustomUser, id=sid, role='student')
  else:
    # A student viewing their own page
    student_user = user

  student_profile = student_user.student_profile

  # 2) Grab all notes (Model.Meta.ordering handles newest-first)
  notes = student_profile.resource_notes.select_related('author').all()

  # 3) Only teachers get to POST a new note
  note_form = None
  if user.role == 'teacher':
    if request.method == 'POST':
      form = ResourceNoteForm(request.POST)
      if form.is_valid():
        note = form.save(commit=False)
        note.student_profile = student_profile
        note.author = user
        note.save()
        notify_resource_note_created(note)   # ← send emails for this new note
        # avoid double-POST: build URL + query and redirect
        base_url = reverse('student_resource')
        return redirect(f"{base_url}?student_id={student_profile.user.id}")
    else:
      form = ResourceNoteForm()
    note_form = form

  return render(request, 'users/student_resources.html', {
    'student_profile': student_profile,
    'notes':           notes,
    'note_form':       note_form,
  })


@login_required
@require_http_methods(["DELETE", "POST"])
def delete_resource_note(request, pk):
  """
  HTMX endpoint to delete a ResourceNote.
  Only the authoring teacher (or an admin) may delete.
  Returns an empty response so HTMX can remove the <div> wrapper.
  """
  note = get_object_or_404(ResourceNote, pk = pk)

  # Ensure only the note’s author or an admin can delete
  if not (
      request.user == note.author
      or request.user.role == 'admin'
      or request.user.role == 'teacher'
    ):
    return HttpResponseForbidden()

  note.delete()
  # HTMX will swap out the element automatically if you
  # set hx-swap="delete" on your delete button.
  return HttpResponse("")


@login_required
@require_http_methods(["GET", "POST"])
def edit_resource_note(request, pk):
  note = get_object_or_404(ResourceNote, pk = pk)

  # only the authoring teacher may edit
  if request.user != note.author or request.user.role != 'teacher':
    return HttpResponseForbidden()

  if request.method == "GET":
    # render a tiny “edit‐in‐place” form fragment
    form = ResourceNoteForm(instance=note)
    return render(request, "users/partials/note_edit_form.html", {
      "note": note,
      "form": form,
    })

  # POST: HTMX sent the form-encoded data in request.POST
  data = request.POST
  
  
  form = ResourceNoteForm(data, instance = note)
  if form.is_valid():
    note = form.save()
    # return the normal read‐only note fragment so HTMX replaces it
    return render(request, "users/partials/note_item.html", {
      "note": note,
    })
  # on validation failure you could re-render the form (with errors)
  return HttpResponse(status=400)


@login_required
def view_resource_note(request, pk):
  """
  HTMX endpoint: re-render the read-only note fragment
  so “Cancel” can swap it back in.
  """
  note = get_object_or_404(ResourceNote, pk = pk)
  return render(request, "users/partials/note_item.html", {
    "note": note,
  })


@login_required
def student_advisors_view(request):
  """
  Displays a list of all advisors (teachers) with sorting and search functionality,
  including name/email, month names, day numbers, month+day, and year filtering.
  """
  # 1) Extract query params
  sort         = request.GET.get('sort', 'user__date_joined')
  order        = request.GET.get('order', 'desc')
  search_query = request.GET.get('search', '').strip()
  items_per_page = int(request.GET.get('items_per_page', 25))
  page_number  = request.GET.get('page', 1)

  # 2) Sort direction
  if order == 'desc':
    sort = f"-{sort}"

  # 3) Base queryset
  advisors = TeacherProfile.objects.select_related('user')

  # 4) “Smart” search
  if search_query:
    q = (
      Q(user__first_name__icontains=search_query) |
      Q(user__last_name__icontains=search_query)  |
      Q(user__email__icontains=search_query)
    )

    # a) Full month name (“June”) or abbrev (“Jun”)
    for fmt in ('%B','%b'):
      try:
        month = datetime.strptime(search_query, fmt).month
        q |= Q(user__date_joined__month=month)
        break
      except ValueError:
        pass

    # b) Day‐of‐month only (“16”)
    if re.fullmatch(r'\d{1,2}', search_query):
      day = int(search_query)
      if 1 <= day <= 31:
        q |= Q(user__date_joined__day=day)

    # c) Month + day (“June 16” / “Jun 16”)
    for fmt in ('%B %d','%b %d'):
      try:
        dt = datetime.strptime(search_query, fmt)
        q |= (
          Q(user__date_joined__month=dt.month) &
          Q(user__date_joined__day=dt.day)
        )
        break
      except ValueError:
        pass

    # d) Year only (“2024”)
    if re.fullmatch(r'\d{4}', search_query):
      q |= Q(user__date_joined__year=int(search_query))

    advisors = advisors.filter(q)

  # 5) Apply sorting safely
  valid = ['user__first_name','user__last_name','user__email','user__date_joined']
  advisors = advisors.order_by(sort if sort.lstrip('-') in valid else 'user__date_joined')

  # 6) Paginate
  paginator = Paginator(advisors, items_per_page)
  page_obj  = paginator.get_page(page_number)

  # 7) Render
  return render(request, 'users/advisor_list.html', {
    'teachers':       page_obj,
    'page_obj':       page_obj,
    'current_sort':   request.GET.get('sort', 'user__date_joined'),
    'current_order':  order,
    'items_per_page': items_per_page,
    'search_query':   search_query,
  })


# View for Listing All Students
@login_required
def teacher_student_list_view(request):
  """
  Displays a list of active students with support for:
  - Sorting (first name, last name, email, date registered, questionnaire status)
  - Searching by name, email, or date registered (month names, days, “Jun 16”, etc)
  - Pagination for better usability
  """
  # 1) Extract query params
  sort = request.GET.get('sort', 'date_joined')
  order = request.GET.get('order', 'desc')
  search_query = request.GET.get('search', '').strip()
  items_per_page = int(request.GET.get('items_per_page', 25))
  page_number   = request.GET.get('page', 1)

  # 2) Sort direction
  if order == 'desc':
    sort = f"-{sort}"

  # 3) Base queryset: only active students, annotate questionnaire status
  students = (
    CustomUser.objects.filter(role='student', is_active=True)
    .select_related('student_profile')
    .annotate(
      questionnaire_completed=Exists(
        Questionnaire.objects.filter(
          student_profile__user=OuterRef('pk'),
          completed=True
        )
      )
    )
  )

  # 4) “Smart” search
  if search_query:
    q = (
      Q(first_name__icontains=search_query) |
      Q(last_name__icontains=search_query)  |
      Q(email__icontains=search_query)
    )

    # a) Month name (“June” or “Jun”)
    for fmt in ('%B','%b'):
      try:
        m = datetime.strptime(search_query, fmt).month
        q |= Q(date_joined__month=m)
        break
      except ValueError:
        pass

    # b) Day‐of‐month only (“16”)
    if re.fullmatch(r'\d{1,2}', search_query):
      day = int(search_query)
      if 1 <= day <= 31:
        q |= Q(date_joined__day=day)

    # c) Month + day (“June 16” or “Jun 16”)
    for fmt in ('%B %d','%b %d'):
      try:
        dt = datetime.strptime(search_query, fmt)
        q |= (
          Q(date_joined__month=dt.month) &
          Q(date_joined__day=dt.day)
        )
        break
      except ValueError:
        pass
      
    # ⇒ d) **Year only** (“2024”, “2025”)
    if re.fullmatch(r'\d{4}', search_query):
      year = int(search_query)
      q |= Q(date_joined__year=year)

    #  d) (Optional) Time strings if you ever record time in student models:
    # if re.fullmatch(r'\d{1,2}:\d{2}', search_query):
    #   q |= Q(date_joined__hour=int(search_query.split(':')[0]))

    students = students.filter(q)

  # 5) Apply sorting
  students = students.order_by(sort)

  # 6) Paginate
  paginator = Paginator(students, items_per_page)
  page_obj  = paginator.get_page(page_number)

  # 7) Render
  return render(request, 'users/student_list.html', {
    'students':     page_obj,
    'page_obj':     page_obj,
    'current_sort': request.GET.get('sort', 'date_joined'),
    'current_order':order,
    'items_per_page':items_per_page,
    'search_query': search_query,
  })


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



class NotifyingPasswordChangeView(PasswordChangeView):
  """
  Wraps Django's PasswordChangeView to send a confirmation email
  after a successful password change.
  """
  # Keep your existing redirect target
  success_url = reverse_lazy("password_change_done")

  # Keep your existing template by passing it in urls.py (below),
  # or set a default here:
  # template_name = "users/password_change.html"

  def form_valid(self, form):
    response = super().form_valid(form)
    notify_password_changed(self.request.user)
    return response