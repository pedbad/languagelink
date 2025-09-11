# -----------------------------------------------------------------------------
# 1) Standard library
# -----------------------------------------------------------------------------
import calendar
import json
import re
from datetime import date, datetime, timedelta
from html import escape

# -----------------------------------------------------------------------------
# 2) Django imports
# -----------------------------------------------------------------------------
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.http import JsonResponse 
from django.shortcuts import render, redirect, get_object_or_404  # get_object_or_404 for advisor filter
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# -----------------------------------------------------------------------------
# 3) Local application imports
# -----------------------------------------------------------------------------
from .models import TeacherAvailability, Booking
from .utils import slot_is_in_past_or_too_soon
from users.utils import has_completed_questionnaire, absolute_avatar_url
from users.models import CustomUser, TeacherProfile  # CustomUser for advisor lookup


@login_required
def teacher_availability_view(request):
  """
  Displays a teacher's availability for a selected month,
  allowing them to toggle slots on/off and view booking details.
  """

  if request.user.role != 'teacher':
    return redirect('teacher_profile')

  year = int(request.GET.get('year', datetime.today().year))
  month = int(request.GET.get('month', datetime.today().month))

  if not (1 <= month <= 12):
    month = datetime.today().month

  _, num_days = calendar.monthrange(year, month)
  month_dates = [
    date(year, month, day)
    for day in range(1, num_days + 1)
    if date(year, month, day).weekday() < 5
  ]

  time_slots = [
    (
      datetime(2000, 1, 1, hour, minute).time(),
      (datetime(2000, 1, 1, hour, minute) + timedelta(minutes=30)).time(),
    )
    for hour in range(9, 18)
    for minute in (0, 30)
  ]

  teacher_availabilities = TeacherAvailability.objects.filter(
    teacher=request.user, date__year=year, date__month=month
  ).select_related("booking__student")

  availability_dict = {}

  for slot in teacher_availabilities:
    key = f"{slot.date.strftime('%Y-%m-%d')},{slot.start_time.strftime('%H:%M:%S')}"

    slot_info = {
      "is_available": slot.is_available,
      "has_booking": False,
      "student_name": None,
      "student_email": None,
      "student_avatar": None,
    }

    if hasattr(slot, "booking"):
      student = slot.booking.student
      slot_info["has_booking"] = True
      slot_info["student_name"]  = f"{student.first_name} {student.last_name}".strip()
      slot_info["student_email"] = student.email
      slot_info["student_message"] = slot.booking.message or ""
      slot_info["student_avatar"] = absolute_avatar_url(request, student)


    availability_dict[key] = slot_info

  # Fill in empty slots with default values
  for day in month_dates:
    day_str = day.strftime('%Y-%m-%d')
    for start_time, _ in time_slots:
      key = f"{day_str},{start_time.strftime('%H:%M:%S')}"
      if key not in availability_dict:
        availability_dict[key] = {
          "is_available": False,
          "has_booking": False,
          "student_name": None,
          "student_email": None,
          "student_avatar": None,
          "student_message": "",
        }

  context = {
    "today": timezone.localdate(),
    "month_dates": month_dates,
    "time_slots": time_slots,
    "availability_dict": availability_dict,
    "current_month": calendar.month_name[month],
    "current_year": year,
    "prev_month": (month - 1) if month > 1 else 12,
    "prev_year": year if month > 1 else year - 1,
    "next_month": (month + 1) if month < 12 else 1,
    "next_year": year if month < 12 else year + 1,
  }

  now_local = timezone.localtime()
  context["now_date"] = now_local.date()
  context["cutoff_time"] = (now_local + timedelta(minutes=settings.BOOKING_LEAD_MINUTES)).time().replace(microsecond=0)

  return render(request, "booking/teacher_availability.html", context)


@csrf_exempt  # Allows AJAX POST requests without CSRF issues
@require_POST
@login_required
def toggle_availability(request):
  """
  Toggles a specific time slot's availability for the logged-in teacher.
  """
  if request.method == "POST":
    try:
      data = json.loads(request.body)

      date_str = data.get("date")
      start_time_str = data.get("start_time")
      end_time_str = data.get("end_time")

      if not all([date_str, start_time_str, end_time_str]):
        return JsonResponse({"error": "Missing required fields"}, status=400)

      slot_date = datetime.strptime(date_str, "%Y-%m-%d").date()
      slot_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
      end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()

      # Ensure the user is a teacher
      if request.user.role != "teacher":
        return JsonResponse({"error": "Unauthorized access"}, status=403)

      # Fetch or create slot
      slot, created = TeacherAvailability.objects.get_or_create(
        teacher=request.user,
        date=slot_date,
        start_time=slot_time,
        end_time=end_time
      )

      # Determine the new state (True = opening the slot)
      new_state = not slot.is_available

      # Block opening if the slot is in the past or within the lead window
      if new_state:
        if slot_is_in_past_or_too_soon(slot.date, slot.start_time):
          return JsonResponse(
            {"success": False, "error": "You can’t open past or too-soon slots."},
            status=400
          )

      # Proceed with the toggle
      slot.is_available = new_state
      slot.save(update_fields=["is_available"])

      # Refresh availability dict for the month (string keys for JSON)
      teacher_availabilities = TeacherAvailability.objects.filter(
        teacher=request.user, date__year=slot_date.year, date__month=slot_date.month
      )
      updated_availability_dict = {
        f"{s.date.strftime('%Y-%m-%d')},{s.start_time.strftime('%H:%M:%S')}": s.is_available
        for s in teacher_availabilities
      }

      return JsonResponse({
        "success": True,
        "is_available": slot.is_available,
        "availability_dict": updated_availability_dict
      })

    except Exception as e:
      print(f"ERROR: {e}")
      return JsonResponse({"error": str(e)}, status=400)

  return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def student_booking_view(request):
  if request.user.role == 'student' and not has_completed_questionnaire(request.user):
    return redirect('questionnaire')  # or HttpResponseForbidden("Please complete the questionnaire first")
  
  # Advisor hint (optional: /booking/bookings/?advisor=123)
  # We only validate/highlight; we do NOT filter the grid by this ID.
  advisor_id = request.GET.get("advisor")
  teacher_user = None
  if advisor_id:
      teacher_user = get_object_or_404(CustomUser, pk=advisor_id, role="teacher")
      # Only allow active advisors to be viewed/filtered
      try:
          tprof = teacher_user.teacher_profile
          if not (tprof.is_active_advisor and (tprof.can_host_online or tprof.can_host_in_person)):
              return redirect("advisors")
      except TeacherProfile.DoesNotExist:
          return redirect("advisors")  
  
  # Get today's date
  today = timezone.localdate()

  # Try to get selected date from query string, fallback to today
  selected_date_str = request.GET.get("date")
  if selected_date_str:
    try:
      selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    except ValueError:
      selected_date = today
  else:
    selected_date = today

  # Determine start and end of the selected week (Monday to Friday)
  week_start = selected_date - timedelta(days=selected_date.weekday())
  week_end = week_start + timedelta(days=4)

  # 🩹 Fix: If navigating to the current week and selected_date is in the past, use today instead
  current_week_start = today - timedelta(days=today.weekday())
  if week_start == current_week_start and selected_date < today:
    selected_date = today

  # Ensure selected_date is still within the visible week boundaries
  if selected_date < week_start or selected_date > week_end:
    selected_date = week_start

  # Calculate previous and next week for navigation
  prev_week = week_start - timedelta(days=7)
  next_week = week_start + timedelta(days=7)

  # Disable "Previous Week" button if already in the current week
  disable_prev_week = week_start <= current_week_start

  # List of dates for the current week (Mon–Fri)
  week_dates = [week_start + timedelta(days=i) for i in range(5)]

  # Disable past days in the current week
  disabled_days = [d for d in week_dates if d < today] if week_start == current_week_start else []

  # Display format for the month/year heading
  if week_start.month == week_end.month:
    month_display = f"{calendar.month_name[week_start.month]} {week_start.year}"
  else:
    month_display = f"{calendar.month_name[week_start.month]} - {calendar.month_name[week_end.month]} {week_end.year}"

  # Generate all 30-min time slots between 9:00–17:30
  time_slots = [
    (
      datetime(2000, 1, 1, hour, minute).time(),
      (datetime(2000, 1, 1, hour, minute) + timedelta(minutes=30)).time()
    )
    for hour in range(9, 18)
    for minute in (0, 30)
  ]

  # === Include slots that are AVAILABLE or already BOOKED on the selected day ===
  day_slots = (
    TeacherAvailability.objects
      .filter(date=selected_date)
      .filter(Q(is_available=True) | Q(booking__isnull=False))
      .filter(
          teacher__role='teacher',
          teacher__teacher_profile__is_active_advisor=True,
      )
      .filter(
          Q(teacher__teacher_profile__can_host_online=True) |
          Q(teacher__teacher_profile__can_host_in_person=True)
      )
      .select_related("teacher", "booking__student", "teacher__teacher_profile")
  )


  teacher_availability_by_email = {}
  teacher_profiles = {}

  for slot in day_slots:
    # thanks to select_related, this doesn't hit the DB again
    profile = slot.teacher.teacher_profile

    # optional belt-and-braces; your queryset already filters to bookable
    if not profile.is_bookable:
        continue

    teacher_email = slot.teacher.email
    key = f"{slot.date.strftime('%Y-%m-%d')},{slot.start_time.strftime('%H:%M:%S')}"
    teacher_availability_by_email.setdefault(teacher_email, {})[key] = slot
    teacher_profiles[teacher_email] = profile

  # Ensure every time slot exists (even if not in DB) for the teachers we kept — for SELECTED DAY ONLY
  date_str = selected_date.strftime('%Y-%m-%d')
  for email in list(teacher_availability_by_email.keys()):
    for start_time, _ in time_slots:
      key = f"{date_str},{start_time.strftime('%H:%M:%S')}"
      if key not in teacher_availability_by_email[email]:
        teacher_availability_by_email[email][key] = None

  # Pass all data to the template
  context = {
    "today": today,
    "selected_date": selected_date,
    "week_dates": week_dates,
    "prev_week": prev_week.strftime("%Y-%m-%d"),
    "next_week": next_week.strftime("%Y-%m-%d"),
    "disable_prev_week": disable_prev_week,
    "disabled_days": disabled_days,
    "month_display": month_display,
    "time_slots": time_slots,
    "teacher_availability_by_email": teacher_availability_by_email,
    "teacher_profiles": teacher_profiles,
    "student_email": request.user.email,
  }

  # Provide 'now' and 'cutoff' for visual disabling in the template
  now_local = timezone.localtime()
  context["now_date"] = now_local.date()
  context["cutoff_time"] = (now_local + timedelta(minutes=settings.BOOKING_LEAD_MINUTES)).time().replace(microsecond=0)
  # expose the current advisor filter to the template
  context["advisor_id"] = teacher_user.id if teacher_user else None

  return render(request, "booking/student_booking_view.html", context)


@login_required
def get_available_slots(request):
    """
    Returns available teachers and their time slots for a given date.
    Only includes teachers who are currently bookable:
      - active advisor
      - offers at least one meeting mode (online or in-person)
    """
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request"}, status=400)

    date_str = request.GET.get("date")
    if not date_str:
        return JsonResponse({"error": "Missing date parameter"}, status=400)

    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"error": "Invalid date format"}, status=400)

    #  Filter to bookable teachers
    available_slots = (
        TeacherAvailability.objects
        .filter(date=selected_date, is_available=True)
        .filter(teacher__role="teacher")
        .filter(teacher__teacher_profile__is_active_advisor=True)
        .filter(
            Q(teacher__teacher_profile__can_host_online=True) |
            Q(teacher__teacher_profile__can_host_in_person=True)
        )
        .select_related("teacher", "teacher__teacher_profile")
    )

    if not available_slots.exists():
        return JsonResponse({"success": True, "slots": {}})

    # Keep the same payload structure: { "HH:MM:SS": [teacher_email, ...], ... }
    slots_dict = {}
    for slot in available_slots:
        time_key = slot.start_time.strftime("%H:%M:%S")
        slots_dict.setdefault(time_key, []).append(slot.teacher.email)

    return JsonResponse({"success": True, "slots": slots_dict})


@csrf_exempt
@require_POST
@login_required
def create_booking(request):
  """Creates a booking for the current student, given a valid availability slot.
  Prevents double-booking and enforces only one booking per day.
  Returns teacher metadata and booking ID for frontend updates.
  """
  # Block bookings until questionnaire is complete
  if getattr(request.user, "role", None) == "student" and not has_completed_questionnaire(request.user):
    return JsonResponse({"error": "Please complete the questionnaire first."}, status=403)

  try:
    data = json.loads(request.body)
    teacher_email = data.get("teacher")
    date_str       = data.get("date")
    start_time_str = data.get("start")
    end_time_str   = data.get("end")
    message        = (data.get("message", "") or "").strip()[:300]  # defensive cap

    if not all([teacher_email, date_str, start_time_str, end_time_str]):
      return JsonResponse({"error": "Missing required data"}, status=400)

    # Only students can create bookings
    if getattr(request.user, "role", None) != "student":
      return JsonResponse({"error": "Unauthorized access"}, status=403)

    # Parse inputs
    slot_date  = datetime.strptime(date_str, "%Y-%m-%d").date()
    start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
    end_time   = datetime.strptime(end_time_str,   "%H:%M:%S").time()

    # Use a transaction and lock the slot row to avoid races
    with transaction.atomic():
      # Lock just the candidate slot
      try:
        slot = (
          TeacherAvailability.objects
          .select_for_update()
          .select_related("teacher", "teacher__teacher_profile")
          .get(
            teacher__email=teacher_email,
            teacher__role="teacher",
            date=slot_date,
            start_time=start_time,
            end_time=end_time,
            is_available=True
          )
        )
      except TeacherAvailability.DoesNotExist:
        return JsonResponse({"error": "This slot is not available"}, status=404)
      
      # ✅ Bookable gate: advisor must be active AND offer at least one meeting mode
      prof = getattr(slot.teacher, "teacher_profile", None)
      if prof is None or not prof.is_active_advisor or not (prof.can_host_online or prof.can_host_in_person):
        return JsonResponse({"error": "This advisor is not currently available to book."}, status=400)

      # Block past/too-soon bookings (do this inside the txn in case time advanced)
      if slot_is_in_past_or_too_soon(slot.date, slot.start_time):
        return JsonResponse({"error": "This slot is no longer available to book."}, status=400)

      # Enforce 1 booking per student per day (check inside the txn to avoid races)
      if Booking.objects.filter(student=request.user, teacher_availability__date=slot_date).exists():
        return JsonResponse({"error": "You already have a booking on this day."}, status=400)

      # Double-booking guard (in case a Booking row already exists)
      if Booking.objects.filter(teacher_availability=slot).exists():
        return JsonResponse({"error": "Slot already booked"}, status=409)

      # Create the booking
      try:
        booking = Booking.objects.create(
          student=request.user,
          teacher_availability=slot,
          message=message
        )
      except IntegrityError:
        # In case of DB uniqueness constraints, surface as conflict
        return JsonResponse({"error": "Slot already booked"}, status=409)

      # Mark the slot as no longer available
      slot.is_available = False
      slot.save(update_fields=["is_available"])

    # Prepare teacher metadata (outside the lock)
    teacher = slot.teacher
    teacher_name = f"{teacher.first_name} {teacher.last_name}".strip()
    teacher_avatar = absolute_avatar_url(request, teacher)


    print("📸 Avatar sent to frontend:", teacher_avatar)

    return JsonResponse({
      "success": True,
      "message": "Booking confirmed!",
      "booking_id": booking.id,
      "teacher_name": teacher_name,
      "teacher_email": teacher.email,
      "teacher_avatar": teacher_avatar,
      "student_message": escape(booking.message),
      "advisor_id": teacher.id,  # preserve advisor context for links
    })

  except Exception as e:
    print("❌ Unexpected error during booking:", str(e))
    return JsonResponse({"error": "An unexpected error occurred."}, status=500)


@login_required
def student_bookings_list(request):
  # only students may stay here
  if request.user.role != "student":
    if request.user.role == "admin":
      return redirect("admin_dashboard")
    if request.user.role == "teacher":
      return redirect("teacher_profile")
    return redirect("login")

  today = date.today()
  upcoming = Booking.objects.filter(
    student=request.user,
    teacher_availability__date__gte=today
  ).select_related(
    "teacher_availability",
    "teacher_availability__teacher"
  ).order_by(
    "teacher_availability__date",
    "teacher_availability__start_time"
  )
  
  # count how many upcoming slots there are
  upcoming_count = upcoming.count()


  past_count = Booking.objects.filter(
      student=request.user,
      teacher_availability__date__lt=today
  ).count()


  # Build a context-friendly list with all needed fields:
  booking_items = []
  for booking in upcoming:
    teacher = booking.teacher_availability.teacher

    # Pick either the teacher’s profile picture or the default:
    avatar_full_url = absolute_avatar_url(request, teacher)

    booking_items.append({
      "date": booking.teacher_availability.date,
      "start_time": booking.teacher_availability.start_time,
      "end_time": booking.teacher_availability.end_time,
      "teacher_name": f"{teacher.first_name} {teacher.last_name}".strip(),
      "teacher_email": teacher.email,
      "teacher_avatar": avatar_full_url,
      "student_message": booking.message or "",
      "teacher_id": teacher.id,
    })

  return render(request, "booking/student_bookings_list.html", {
    "bookings": booking_items,
    "upcoming_count": upcoming_count,
    "past_count": past_count,
    "show_past": False,
    "list_url":  "student_bookings_list",
    "past_url":  "student_bookings_past",
  })
  
  
@login_required
def teacher_bookings_list(request):
  # only teachers may stay here
  if request.user.role != "teacher":
    if request.user.role == "admin":
      return redirect("admin_dashboard")
    if request.user.role == "student":
      return redirect("student_profile")
    return redirect("login")

  today = date.today()
  search_query = request.GET.get("search", "").strip()

  # Base queryset
  qs = Booking.objects.filter(
      teacher_availability__teacher=request.user,
      teacher_availability__date__gte=today
    ) \
    .select_related("teacher_availability", "student", "student__student_profile")

  if search_query:
    # name/email
    q = (
      Q(student__first_name__icontains=search_query) |
      Q(student__last_name__icontains=search_query)  |
      Q(student__email__icontains=search_query)
    )

    # time HH:MM
    if re.match(r'^\d{1,2}:\d{2}$', search_query):
      q |= Q(teacher_availability__start_time__startswith=search_query) \
         | Q(teacher_availability__end_time__startswith=search_query)

    # month name (“June” or “Jun”)
    for fmt in ('%B','%b'):
      try:
        m = datetime.strptime(search_query, fmt).month
        q |= Q(teacher_availability__date__month=m)
        break
      except ValueError:
        pass

    # day-of-month only (“16”)
    if re.match(r'^\d{1,2}$', search_query):
      day = int(search_query)
      if 1 <= day <= 31:
        q |= Q(teacher_availability__date__day=day)

    # 5) month + day (“June 16” or “Jun 16”)
    for fmt in ('%B %d','%b %d'):
      try:
        dt = datetime.strptime(search_query, fmt)
        q |= (
          Q(teacher_availability__date__month=dt.month) &
          Q(teacher_availability__date__day=dt.day)
        )
        break
      except ValueError:
        pass

    qs = qs.filter(q)

  upcoming = qs.order_by(
    "teacher_availability__date",
    "teacher_availability__start_time"
  )
  
  # how many future vs past?
  upcoming_count = upcoming.count()
  past_count = Booking.objects.filter(
    teacher_availability__teacher=request.user,
    teacher_availability__date__lt=today
  ).count()

  booking_items = []
  for booking in upcoming:
    student = booking.student
    avatar = absolute_avatar_url(request, student)


    booking_items.append({
      "date":            booking.teacher_availability.date,
      "start_time":      booking.teacher_availability.start_time,
      "end_time":        booking.teacher_availability.end_time,
      "student_name":    f"{student.first_name} {student.last_name}".strip(),
      "student_email":   student.email,
      "student_avatar":  avatar,
      "student_message": booking.message or "",
      "student_id":      student.id,
    })

  return render(request, "booking/teacher_bookings_list.html", {
    "bookings": booking_items,
    "search_query": search_query,
    "upcoming_count": upcoming_count,
    "past_count": past_count,
    "show_past": False,
    "list_url": "teacher_bookings_list",
    "past_url": "teacher_bookings_past",
  })
  

@login_required
def admin_bookings_list(request):
  # only admins may stay here
  if request.user.role != "admin":
    if request.user.role == "teacher":
      return redirect("teacher_profile")
    if request.user.role == "student":
      return redirect("student_profile")
    return redirect("login")

  # Sorting params
  sort_key = request.GET.get("sort", "date")   # "date", "adv_name", or "stu_name"
  order    = request.GET.get("order", "asc")   # "asc" or "desc"

  today  = date.today()
  q_text = request.GET.get("search", "").strip()

  # Base queryset
  qs = Booking.objects.filter(
      teacher_availability__date__gte = today
    ).select_related(
      "teacher_availability",
      "teacher_availability__teacher",
      "teacher_availability__teacher__teacher_profile",
      "student",
      "student__student_profile",
    )


  # 3) “Smart” search
  if q_text:
    q = (
      Q(student__first_name__icontains = q_text) |
      Q(student__last_name__icontains = q_text)  |
      Q(student__email__icontains = q_text)     |
      Q(teacher_availability__teacher__first_name__icontains = q_text) |
      Q(teacher_availability__teacher__last_name__icontains = q_text)  |
      Q(teacher_availability__teacher__email__icontains = q_text)
    )

    # time “HH:MM”
    if re.fullmatch(r"\d{1,2}:\d{2}", q_text):
      q |= (
        Q(teacher_availability__start_time__startswith = q_text) |
        Q(teacher_availability__end_time__startswith = q_text)
      )

    # month name “June” / “Jun”
    for fmt in ("%B","%b"):
      try:
        m = datetime.strptime(q_text, fmt).month
        q |= Q(teacher_availability__date__month=m)
        break
      except ValueError:
        pass

    # day‐of‐month only “16”
    if re.fullmatch(r"\d{1,2}", q_text):
      d = int(q_text)
      if 1 <= d <= 31:
        q |= Q(teacher_availability__date__day=d)

    # year only “2024”
    if re.fullmatch(r"\d{4}", q_text):
      q |= Q(teacher_availability__date__year = int(q_text))

    # full “Month Day” “June 16”
    for fmt in ("%B %d","%b %d"):
      try:
        dt = datetime.strptime(q_text, fmt)
        q |= (
          Q(teacher_availability__date__month = dt.month) &
          Q(teacher_availability__date__day = dt.day)
        )
        break
      except ValueError:
        pass

    qs = qs.filter(q)

  # Apply sorting
  if sort_key == "date":
    if order == "asc":
      qs = qs.order_by("teacher_availability__date",
                       "teacher_availability__start_time")
    else:
      qs = qs.order_by("-teacher_availability__date",
                       "-teacher_availability__start_time")

  elif sort_key == "adv_name":
    prefix = "" if order == "asc" else "-"
    qs = qs.order_by(
      f"{prefix}teacher_availability__teacher__first_name",
      f"{prefix}teacher_availability__teacher__last_name"
    )

  elif sort_key == "stu_name":
    prefix = "" if order == "asc" else "-"
    qs = qs.order_by(
      f"{prefix}student__first_name",
      f"{prefix}student__last_name"
    )

  else:
    # fallback to date
    qs = qs.order_by("teacher_availability__date",
                     "teacher_availability__start_time")

  # Build flat list for template
  items = []
  for b in qs:
    s = b.student
    t = b.teacher_availability.teacher

    #  avatars
    stu_avatar = absolute_avatar_url(request, s)
    adv_avatar = absolute_avatar_url(request, t)


    items.append({
      "date": b.teacher_availability.date,
      "start": b.teacher_availability.start_time,
      "end": b.teacher_availability.end_time,
      "stu_name": f"{s.first_name} {s.last_name}".strip(),
      "stu_email": s.email,
      "stu_avatar": stu_avatar,
      "adv_name": f"{t.first_name} {t.last_name}".strip(),
      "adv_email": t.email,
      "adv_avatar": adv_avatar,
      "adv_id": t.id,
      "stu_id": s.id,
      "message": b.message or "",
    })
    
  # Counts for badges
  upcoming_count = Booking.objects.filter(
      teacher_availability__date__gte=today
  ).count()
  past_count = Booking.objects.filter(
      teacher_availability__date__lt=today
  ).count()

  # Render with current_sort/order for the header arrows
  return render(request, "booking/admin_bookings_list.html", {
    "bookings": items,
    "search_query": q_text,
    "current_sort": sort_key,
    "current_order": order,
    "show_past": False,
    "list_url": "admin_bookings_list",
    "past_url": "admin_bookings_past",
    "upcoming_count": upcoming_count,
    "past_count": past_count,
  })
  
  
@login_required
def student_bookings_past(request):
  if request.user.role != "student":
    if request.user.role == "admin":
      return redirect("admin_dashboard")
    if request.user.role == "teacher":
      return redirect("teacher_profile")
    return redirect("login")  
    
  today = date.today()

  past_qs = Booking.objects.filter(
    student=request.user,
    teacher_availability__date__lt=today
  ).select_related(
    "teacher_availability", "teacher_availability__teacher"
  ).order_by(
    "-teacher_availability__date",
    "-teacher_availability__start_time"
  )

  # build items exactly as in student_bookings_list…
  booking_items = []
  for b in past_qs:
    t = b.teacher_availability.teacher
    avatar = absolute_avatar_url(request, t)

    booking_items.append({
      "date":        b.teacher_availability.date,
      "start_time":  b.teacher_availability.start_time,
      "end_time":    b.teacher_availability.end_time,
      "teacher_name":f"{t.first_name} {t.last_name}".strip(),
      "teacher_email":t.email,
      "teacher_avatar":avatar,
      "student_message": b.message or "",
      "teacher_id":  t.id,
    })

  # also compute how many upcoming remain, so the toggle link can show “Upcoming (N)”
  upcoming_count = Booking.objects.filter(
    student=request.user,
    teacher_availability__date__gte=today
  ).count()

  return render(request, "booking/student_bookings_past.html", {
    "bookings": booking_items,
    "past_count": past_qs.count(),
    "upcoming_count": upcoming_count,
    "show_past": True,
    "list_url": "student_bookings_list",
    "past_url": "student_bookings_past",
  })
  
  
@login_required
def teacher_bookings_past(request):
  # only teachers stay here
  if request.user.role != "teacher":
    if request.user.role == "admin":
      return redirect("admin_dashboard")
    if request.user.role == "student":
      return redirect("student_profile")
    return redirect("login")

  today = date.today()
  past_qs = Booking.objects.filter(
    teacher_availability__teacher=request.user,
    teacher_availability__date__lt=today
  ).select_related(
    "teacher_availability",
    "student",
    "student__student_profile"
  ).order_by(
    "-teacher_availability__date",
    "-teacher_availability__start_time"
  )

  # build the same flat list shape
  booking_items = []
  for b in past_qs:
    student = b.student
    avatar = absolute_avatar_url(request, student)


    booking_items.append({
      "date":           b.teacher_availability.date,
      "start_time":     b.teacher_availability.start_time,
      "end_time":       b.teacher_availability.end_time,
      "student_name":   f"{student.first_name} {student.last_name}".strip(),
      "student_email":  student.email,
      "student_avatar": avatar,
      "student_message": b.message or "",
      "student_id":     student.id,
    })

  # counts for toggle
  upcoming_count = Booking.objects.filter(
    teacher_availability__teacher=request.user,
    teacher_availability__date__gte=today
  ).count()
  past_count = past_qs.count()

  return render(request, "booking/teacher_bookings_past.html", {
    "bookings":       booking_items,
    "upcoming_count": upcoming_count,
    "past_count":     past_count,
    "show_past":      True,
    "list_url":       "teacher_bookings_list",
    "past_url":       "teacher_bookings_past",
    "search_query":   "",   # optional: keep same context shape
  })
  

@login_required
def admin_bookings_past(request):
  # restrict view to admins
  if request.user.role != "admin":
    if request.user.role == "teacher":
      return redirect("teacher_profile")
    if request.user.role == "student":
      return redirect("student_profile")
    return redirect("login")

  # parse query parameters
  today = date.today()
  sort_key = request.GET.get("sort", "date")
  order = request.GET.get("order", "asc")
  search_query = request.GET.get("search", "").strip()

  # base queryset: past bookings only
  qs = Booking.objects.filter(
    teacher_availability__date__lt=today
  ).select_related(
    "teacher_availability",
    "teacher_availability__teacher",
    "teacher_availability__teacher__teacher_profile",
    "student",
    "student__student_profile"
  )


  # apply search filters
  if search_query:
    q = (
      Q(student__first_name__icontains=search_query) |
      Q(student__last_name__icontains=search_query) |
      Q(student__email__icontains=search_query) |
      Q(teacher_availability__teacher__first_name__icontains=search_query) |
      Q(teacher_availability__teacher__last_name__icontains=search_query) |
      Q(teacher_availability__teacher__email__icontains=search_query)
    )
    # TODO: add time/month/day/year parsing here
    qs = qs.filter(q)

  # apply sorting
  prefix = "" if order == "asc" else "-"
  if sort_key == "date":
    qs = qs.order_by(
      f"{prefix}teacher_availability__date",
      f"{prefix}teacher_availability__start_time"
    )
  elif sort_key == "adv_name":
    qs = qs.order_by(
      f"{prefix}teacher_availability__teacher__first_name",
      f"{prefix}teacher_availability__teacher__last_name"
    )
  elif sort_key == "stu_name":
    qs = qs.order_by(
      f"{prefix}student__first_name",
      f"{prefix}student__last_name"
    )
  else:
    qs = qs.order_by(
      "teacher_availability__date",
      "teacher_availability__start_time"
    )

  # build list of bookings for template
  items = []
  for booking in qs:
    student = booking.student
    teacher = booking.teacher_availability.teacher

    student_avatar = absolute_avatar_url(request, student)
    teacher_avatar = absolute_avatar_url(request, teacher)

    items.append({
      "date": booking.teacher_availability.date,
      "start": booking.teacher_availability.start_time,
      "end": booking.teacher_availability.end_time,
      "stu_name": f"{student.first_name} {student.last_name}".strip(),
      "stu_email": student.email,
      "stu_avatar": student_avatar,
      "adv_name": f"{teacher.first_name} {teacher.last_name}".strip(),
      "adv_email": teacher.email,
      "adv_avatar": teacher_avatar,
      "adv_id": teacher.id,
      "stu_id": student.id,
      "message": booking.message or ""
    })

  # counts for toggle badges
  upcoming_count = Booking.objects.filter(
    teacher_availability__date__gte=today
  ).count()
  past_count = qs.count()

  # render with toggle context
  return render(request, "booking/admin_bookings_list.html", {
    "bookings": items,
    "search_query": search_query,
    "current_sort": sort_key,
    "current_order": order,
    "show_past": True,
    "list_url": "admin_bookings_list",
    "past_url": "admin_bookings_past",
    "upcoming_count": upcoming_count,
    "past_count": past_count,
  })


