from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST  # Add this to enforce POST requests
from datetime import datetime, timedelta, date
import calendar
import json
from .models import TeacherAvailability, Booking


@login_required
def teacher_availability_view(request):
  """
  Displays a teacher's availability for a selected month,
  allowing them to toggle slots on/off.
  """

  # Restrict access to teachers only
  if request.user.role != 'teacher':
    return redirect('teacher_profile')

  # Get year and month from query params (default to current month)
  year = int(request.GET.get('year', datetime.today().year))
  month = int(request.GET.get('month', datetime.today().month))

  # Ensure the month is valid (1-12)
  if not (1 <= month <= 12):
    month = datetime.today().month  # Fallback to current month

  print(f"DEBUG: Loading availability for {calendar.month_name[month]} ({month})")

  # Get total days in the month and filter out weekends (Mon-Fri only)
  _, num_days = calendar.monthrange(year, month)
  month_dates = [
    date(year, month, day)
    for day in range(1, num_days + 1)
    if date(year, month, day).weekday() < 5  # Exclude weekends
  ]

  # Define 30-minute slots from 9:00 AM to 5:30 PM
  time_slots = [
    (
      datetime(2000, 1, 1, hour, minute).time(),
      (datetime(2000, 1, 1, hour, minute) + timedelta(minutes=30)).time(),
    )
    for hour in range(9, 18)  # 9:00 AM - 5:30 PM
    for minute in (0, 30)
  ]

  # Fetch existing availability records for the teacher
  teacher_availabilities = TeacherAvailability.objects.filter(
    teacher=request.user, date__year=year, date__month=month
  )

  print(f"DEBUG: Retrieved Availability - {list(teacher_availabilities.values())}")

  # Convert queryset to dictionary for quick lookup
  # availability_dict = {
  #   f"{slot.date.strftime('%Y-%m-%d')},{slot.start_time.strftime('%H:%M:%S')}": slot.is_available
  #   for slot in teacher_availabilities
  # }
  availability_dict = {
    f"{slot.date.strftime('%Y-%m-%d')},{slot.start_time.strftime('%H:%M:%S')}": slot
    for slot in teacher_availabilities
  }


  print(f"DEBUG: Final Availability Dictionary - {availability_dict}")

  # Ensure all slots exist, defaulting to False if not stored in the DB
  for day in month_dates:
    day_str = day.strftime('%Y-%m-%d')
    for start_time, _ in time_slots:
      key = f"{day_str},{start_time.strftime('%H:%M:%S')}"
      if key not in availability_dict:
        availability_dict[key] = None  # default to None

  # Prepare context for rendering the template
  context = {
    "today": date.today(),
    "month_dates": month_dates,
    "time_slots": time_slots,
    "availability_dict": availability_dict,  # Pass availability to template
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

  print("DEBUG: Toggle Availability View Hit!")

  if request.method == "POST":
    try:
      data = json.loads(request.body)
      print(f"DEBUG: Received Data - {data}")

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

      print(f"DEBUG: Before Toggle - Exists: {not created}, Available: {slot.is_available}")

      slot.is_available = not slot.is_available
      slot.save(update_fields=['is_available'])  # Save only `is_available` field

      print(f"DEBUG: After Toggle - Updated Slot: {slot.date}, {slot.start_time}, Available: {slot.is_available}")

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

  print("DEBUG: Invalid Request Method")
  return JsonResponse({"error": "Invalid request"}, status=400)

  """
  Toggles a specific time slot's availability for the logged-in teacher.
  """

  print("DEBUG: Toggle Availability View Hit!")

  if request.method == "POST":
    try:
      data = json.loads(request.body)
      print(f"DEBUG: Received Data - {data}")

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

      print(f"DEBUG: Before Toggle - Exists: {not created}, Available: {slot.is_available}")

      slot.is_available = not slot.is_available
      slot.save(update_fields=['is_available'])  # Save only `is_available` field

      print(f"DEBUG: After Toggle - Updated Slot: {slot.date}, {slot.start_time}, Available: {slot.is_available}")

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

  print("DEBUG: Invalid Request Method")
  return JsonResponse({"error": "Invalid request"}, status=400)

  """
  Toggles a specific time slot's availability for the logged-in teacher.
  """

  print("DEBUG: Toggle Availability View Hit!")

  if request.method == "POST":
    try:
      data = json.loads(request.body)
      print(f"DEBUG: Received Data - {data}")

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

      print(f"DEBUG: Before Toggle - Exists: {not created}, Available: {slot.is_available}")

      slot.is_available = not slot.is_available
      slot.save(update_fields=['is_available'])  # Save only `is_available` field

      print(f"DEBUG: After Toggle - Updated Slot: {slot.date}, {slot.start_time}, Available: {slot.is_available}")

      return JsonResponse({"success": True, "is_available": slot.is_available})

    except Exception as e:
      print(f"ERROR: {e}")  # Log any errors
      return JsonResponse({"error": str(e)}, status=400)

  print("DEBUG: Invalid Request Method")
  return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def student_booking_view(request):
  # Only allow access to students
  # if request.user.role != "student":
  #   return redirect("student_profile")

  today = date.today()

  # Get selected date from query parameter or default to today
  selected_date_str = request.GET.get("date")
  if selected_date_str:
    try:
      selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    except ValueError:
      selected_date = today
  else:
    selected_date = today

  # Week calculations (Monday to Friday)
  week_start = selected_date - timedelta(days=selected_date.weekday())
  week_end = week_start + timedelta(days=4)
  prev_week = week_start - timedelta(days=7)
  next_week = week_start + timedelta(days=7)

  # Disable back navigation to weeks before current week
  current_week_start = today - timedelta(days=today.weekday())
  disable_prev_week = week_start <= current_week_start

  # Generate list of weekdays in the current view
  week_dates = [week_start + timedelta(days=i) for i in range(5)]
  disabled_days = [d for d in week_dates if d < today] if week_start == current_week_start else []

  # Month/year display
  if week_start.month == week_end.month:
    month_display = f"{calendar.month_name[week_start.month]} {week_start.year}"
  else:
    month_display = f"{calendar.month_name[week_start.month]} - {calendar.month_name[week_end.month]} {week_end.year}"

  # Generate all 30-min time slots from 9:00 to 17:30
  time_slots = [
    (
      datetime(2000, 1, 1, hour, minute).time(),
      (datetime(2000, 1, 1, hour, minute) + timedelta(minutes=30)).time()
    )
    for hour in range(9, 18)
    for minute in (0, 30)
  ]

  # Fetch ALL availability (not just available=True) for the current week
  all_slots = TeacherAvailability.objects.filter(
    date__range=(week_start, week_end)
  ).select_related("teacher").select_related("booking")  # ✅ Add this if missing

  # 🧠 Build: teacher_email → { "YYYY-MM-DD,HH:MM:SS": True/False }
  teacher_availability_by_teacher = {}

  # First populate actual availability from DB — only for active advisors
  for slot in all_slots:
    try:
      profile = slot.teacher.teacherprofile
      if not profile.is_active_advisor:
        continue  # 🚫 skip inactive advisors

      key = f"{slot.date.strftime('%Y-%m-%d')},{slot.start_time.strftime('%H:%M:%S')}"
      teacher_availability_by_teacher.setdefault(profile, {})[key] = slot  # Save the slot object, not just True/False

    except TeacherProfile.DoesNotExist:
      continue  # skip teachers with no profile

  # Ensure full week × time_slots coverage per teacher (default to False if not set)
  for email in teacher_availability_by_teacher.keys():
    for day in week_dates:
      date_str = day.strftime('%Y-%m-%d')
      for start_time, _ in time_slots:
        key = f"{date_str},{start_time.strftime('%H:%M:%S')}"
        if key not in teacher_availability_by_teacher[email]:
          teacher_availability_by_teacher[email][key] = False


  # 📦 Final context for template
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
    "teacher_availability_by_teacher": teacher_availability_by_teacher,
  }
  
  import pprint
  pprint.pprint(teacher_availability_by_teacher)

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
  """
  try:
    data = json.loads(request.body)
    teacher_email = data.get("teacher")
    date_str = data.get("date")
    start_time_str = data.get("start")
    end_time_str = data.get("end")

    if not all([teacher_email, date_str, start_time_str, end_time_str]):
      return JsonResponse({"error": "Missing required data"}, status=400)

    # Parse strings to Python types
    slot_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
    end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()

    # Check for existing booking by this student on the same date
    existing_booking = Booking.objects.filter(
      student=request.user,
      teacher_availability__date=slot_date
    ).exists()

    if existing_booking:
      return JsonResponse({
        "error": "You already have a booking on this day."
      }, status=400)

    # Look up the availability slot
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

    # Check if already booked
    if hasattr(slot, "booking"):
      return JsonResponse({"error": "Slot already booked"}, status=409)

    # Create the booking
    Booking.objects.create(
      student=request.user,
      teacher_availability=slot
    )

    # Optionally mark the slot as unavailable (one-time slot)
    slot.is_available = False
    slot.save(update_fields=["is_available"])

    return JsonResponse({"success": True, "message": "Booking confirmed!"})

  except Exception as e:
    return JsonResponse({"error": str(e)}, status=500)
