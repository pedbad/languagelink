# Python stdlib
import json
import calendar
from datetime import datetime, timedelta, date
from urllib.parse import urlparse

# Django core
from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage

# Local app
from .models import TeacherAvailability, Booking


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
      slot_info["student_name"] = f"{student.first_name} {student.last_name}".strip()
      slot_info["student_email"] = student.email

      try:
        profile = student.studentprofile
        if profile.profile_picture:
          avatar_url = profile.profile_picture.url
          if avatar_url.startswith("/"):
            avatar_url = request.build_absolute_uri(avatar_url)
          slot_info["student_avatar"] = avatar_url
        else:
          slot_info["student_avatar"] = request.build_absolute_uri("/static/core/img/default-profile.png")
      except:
        slot_info["student_avatar"] = request.build_absolute_uri("/static/core/img/default-profile.png")

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
        }

  context = {
    "today": date.today(),
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

  return render(request, "booking/teacher_availability.html", context)


@csrf_exempt  # Allows AJAX POST requests without CSRF issues
@login_required
def toggle_availability(request):
  """
  Toggles a specific time slot's availability for the logged-in teacher.
  """

  #print("DEBUG: Toggle Availability View Hit!")

  if request.method == "POST":
    try:
      data = json.loads(request.body)
      #print(f"DEBUG: Received Data - {data}")

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

      # Fetch or create slot, then toggle availability
      slot, created = TeacherAvailability.objects.get_or_create(
        teacher=request.user,
        date=slot_date,
        start_time=slot_time,
        end_time=end_time
      )

      #print(f"DEBUG: Before Toggle - Exists: {not created}, Available: {slot.is_available}")

      slot.is_available = not slot.is_available
      slot.save(update_fields=['is_available'])  # Save only `is_available` field

      #print(f"DEBUG: After Toggle - Updated Slot: {slot.date}, {slot.start_time}, Available: {slot.is_available}")

      # Convert availability_dict keys into **strings** (JSON-safe)
      teacher_availabilities = TeacherAvailability.objects.filter(
        teacher=request.user, date__year=slot_date.year, date__month=slot_date.month
      )

      updated_availability_dict = {
        f"{slot.date.strftime('%Y-%m-%d')},{slot.start_time.strftime('%H:%M:%S')}": slot.is_available
        for slot in teacher_availabilities
      }

      return JsonResponse({
        "success": True, 
        "is_available": slot.is_available, 
        "availability_dict": updated_availability_dict  # Now has string keys
      })

    except Exception as e:
      print(f"ERROR: {e}")  # Log any errors
      return JsonResponse({"error": str(e)}, status=400)

  #print("DEBUG: Invalid Request Method")
  return JsonResponse({"error": "Invalid request"}, status=400)

  """
  Toggles a specific time slot's availability for the logged-in teacher.
  """

  #print("DEBUG: Toggle Availability View Hit!")

  if request.method == "POST":
    try:
      data = json.loads(request.body)
      #print(f"DEBUG: Received Data - {data}")

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

      # Fetch or create slot, then toggle availability
      slot, created = TeacherAvailability.objects.get_or_create(
        teacher=request.user,
        date=slot_date,
        start_time=slot_time,
        end_time=end_time
      )

      #print(f"DEBUG: Before Toggle - Exists: {not created}, Available: {slot.is_available}")

      slot.is_available = not slot.is_available
      slot.save(update_fields=['is_available'])  # Save only `is_available` field

      #print(f"DEBUG: After Toggle - Updated Slot: {slot.date}, {slot.start_time}, Available: {slot.is_available}")

      # Return the entire updated availability dictionary
      teacher_availabilities = TeacherAvailability.objects.filter(
        teacher=request.user, date__year=slot_date.year, date__month=slot_date.month
      )

      updated_availability_dict = {
        (slot.date.strftime('%Y-%m-%d'), slot.start_time.strftime('%H:%M:%S')): slot.is_available
        for slot in teacher_availabilities
      }

      return JsonResponse({
        "success": True, 
        "is_available": slot.is_available, 
        "availability_dict": updated_availability_dict  # Send updated data
      })

    except Exception as e:
      print(f"ERROR: {e}")  # Log any errors
      return JsonResponse({"error": str(e)}, status=400)

  #print("DEBUG: Invalid Request Method")
  return JsonResponse({"error": "Invalid request"}, status=400)

  """
  Toggles a specific time slot's availability for the logged-in teacher.
  """

  #print("DEBUG: Toggle Availability View Hit!")

  if request.method == "POST":
    try:
      data = json.loads(request.body)
      #print(f"DEBUG: Received Data - {data}")

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

      # Fetch or create slot, then toggle availability
      slot, created = TeacherAvailability.objects.get_or_create(
        teacher=request.user,
        date=slot_date,
        start_time=slot_time,
        end_time=end_time
      )

      #print(f"DEBUG: Before Toggle - Exists: {not created}, Available: {slot.is_available}")

      slot.is_available = not slot.is_available
      slot.save(update_fields=['is_available'])  # Save only `is_available` field

      #print(f"DEBUG: After Toggle - Updated Slot: {slot.date}, {slot.start_time}, Available: {slot.is_available}")

      return JsonResponse({"success": True, "is_available": slot.is_available})

    except Exception as e:
      print(f"ERROR: {e}")  # Log any errors
      return JsonResponse({"error": str(e)}, status=400)

  #print("DEBUG: Invalid Request Method")
  return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def student_booking_view(request):
  # Get today's date
  today = date.today()

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

  # Fetch all availability slots in the selected week, along with related teacher and booking
  all_slots = TeacherAvailability.objects.filter(
    date__range=(week_start, week_end)
  ).select_related("teacher", "booking")

  teacher_availability_by_email = {}
  teacher_profiles = {}

  # Organize slots by teacher email and day+time key
  for slot in all_slots:
    try:
      profile = slot.teacher.teacherprofile
      if not profile.is_active_advisor:
        continue  # Skip inactive advisors

      teacher_email = slot.teacher.email
      key = f"{slot.date.strftime('%Y-%m-%d')},{slot.start_time.strftime('%H:%M:%S')}"

      teacher_availability_by_email.setdefault(teacher_email, {})[key] = slot
      teacher_profiles[teacher_email] = profile

    except TeacherProfile.DoesNotExist:
      continue  # Skip teachers without profiles

  # Ensure every time slot exists (even if not in DB)
  for email in teacher_availability_by_email.keys():
    for day in week_dates:
      date_str = day.strftime('%Y-%m-%d')
      for start_time, _ in time_slots:
        key = f"{date_str},{start_time.strftime('%H:%M:%S')}"
        if key not in teacher_availability_by_email[email]:
          teacher_availability_by_email[email][key] = None

  # Debug print of final availability structure (optional)
  # import pprint
  # pprint.pprint(teacher_availability_by_email)

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

  return render(request, "booking/student_booking_view.html", context)


@login_required
def get_available_slots(request):
  """
  Returns available teachers and their time slots for a given date.
  """

  # Ensure the request is a GET request
  if request.method != "GET":
    return JsonResponse({"error": "Invalid request"}, status=400)

  # Get the date parameter from the request
  date_str = request.GET.get("date")
  if not date_str:
    return JsonResponse({"error": "Missing date parameter"}, status=400)

  try:
    selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
  except ValueError:
    return JsonResponse({"error": "Invalid date format"}, status=400)

  # Fetch available slots for the selected date
  available_slots = TeacherAvailability.objects.filter(
    date=selected_date, is_available=True
  ).select_related("teacher")

  if not available_slots.exists():
    return JsonResponse({"success": True, "slots": {}})  # Return empty slots if none exist

  # Convert the queryset into a structured dictionary
  slots_dict = {}
  for slot in available_slots:
    time_key = slot.start_time.strftime("%H:%M:%S")
    if time_key not in slots_dict:
      slots_dict[time_key] = []

    slots_dict[time_key].append(slot.teacher.email)

  return JsonResponse({"success": True, "slots": slots_dict})


@csrf_exempt
@require_POST
@login_required
def create_booking(request):
  """
  Creates a booking for the current student, given a valid availability slot.
  Prevents double-booking and enforces only one booking per day.
  Returns teacher metadata and booking ID for frontend updates.
  """
  try:
    data = json.loads(request.body)
    teacher_email = data.get("teacher")
    date_str = data.get("date")
    start_time_str = data.get("start")
    end_time_str = data.get("end")

    if not all([teacher_email, date_str, start_time_str, end_time_str]):
      return JsonResponse({"error": "Missing required data"}, status=400)

    # Parse string inputs
    slot_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
    end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()

    # Enforce 1 booking per student per day
    if Booking.objects.filter(student=request.user, teacher_availability__date=slot_date).exists():
      return JsonResponse({
        "error": "You already have a booking on this day."
      }, status=400)

    # Get the available slot
    try:
      slot = TeacherAvailability.objects.get(
        teacher__email=teacher_email,
        date=slot_date,
        start_time=start_time,
        end_time=end_time,
        is_available=True
      )
    except TeacherAvailability.DoesNotExist:
      return JsonResponse({"error": "This slot is not available"}, status=404)

    # Prevent double booking
    if hasattr(slot, "booking"):
      return JsonResponse({"error": "Slot already booked"}, status=409)

    # Create booking
    booking = Booking.objects.create(
      student=request.user,
      teacher_availability=slot
    )

    # Mark slot as unavailable
    slot.is_available = False
    slot.save(update_fields=["is_available"])

    # Prepare teacher metadata
    teacher = slot.teacher
    teacher_name = f"{teacher.first_name} {teacher.last_name}".strip()
    default_avatar = "/static/core/img/default-profile.png"
    teacher_avatar = default_avatar

    try:
      profile = teacher.teacherprofile
      if profile.profile_picture:
        try:
          avatar_url = profile.profile_picture.url

          # Optional check for production; skip in dev
          is_dev = settings.DEBUG and settings.MEDIA_URL in avatar_url

          if is_dev or default_storage.exists(profile.profile_picture.name):
            teacher_avatar = avatar_url

        except Exception as img_err:
          print("⚠️ Avatar resolution error:", img_err)

    except TeacherProfile.DoesNotExist:
      pass

    # Normalize to absolute URL
    if teacher_avatar.startswith("/"):
      teacher_avatar = request.build_absolute_uri(teacher_avatar)

    print("📸 Avatar sent to frontend:", teacher_avatar)

    return JsonResponse({
      "success": True,
      "message": "Booking confirmed!",
      "booking_id": booking.id,
      "teacher_name": teacher_name,
      "teacher_email": teacher.email,
      "teacher_avatar": teacher_avatar,
    })

  except Exception as e:
    print("❌ Unexpected error during booking:", str(e))
    return JsonResponse({"error": "An unexpected error occurred."}, status=500)
