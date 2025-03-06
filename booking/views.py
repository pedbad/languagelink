from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
  availability_dict = {
    f"{slot.date.strftime('%Y-%m-%d')},{slot.start_time.strftime('%H:%M:%S')}": slot.is_available
    for slot in teacher_availabilities
  }

  print(f"DEBUG: Final Availability Dictionary - {availability_dict}")

  # Ensure all slots exist, defaulting to False if not stored in the DB
  for day in month_dates:
    day_str = day.strftime('%Y-%m-%d')
    for start_time, _ in time_slots:
      key = f"{day_str},{start_time.strftime('%H:%M:%S')}"
      if key not in availability_dict:
        availability_dict[key] = False  # Default to False

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

      # ✅ Convert availability_dict keys into **strings** (JSON-safe)
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
        "availability_dict": updated_availability_dict  # ✅ Now has string keys
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

      # ✅ Return the entire updated availability dictionary
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
  """
  Displays available booking slots for students, showing available teachers per slot.
  """

  # Restrict access to students only
  if request.user.role != 'student':
    return redirect('student_dashboard')

  # Get current date and determine week's range
  today = date.today()
  start_of_week = today - timedelta(days=today.weekday())  # Get Monday
  selected_week = int(request.GET.get("week", 0))  # Default to current week

  # Calculate the week's date range
  start_date = start_of_week + timedelta(weeks=selected_week)
  end_date = start_date + timedelta(days=4)  # Friday only (no weekends)

  # Generate weekdays list (Monday to Friday)
  week_dates = [start_date + timedelta(days=i) for i in range(5)]

  # Define 30-minute slots from 9:00 AM to 5:30 PM
  time_slots = [
    (
      datetime(2000, 1, 1, hour, minute).time(),
      (datetime(2000, 1, 1, hour, minute) + timedelta(minutes=30)).time(),
    )
    for hour in range(9, 18)  # 9:00 AM - 5:30 PM
    for minute in (0, 30)
  ]

  # Fetch all available slots for this week
  available_slots = TeacherAvailability.objects.filter(
    date__range=[start_date, end_date],
    is_available=True
  ).select_related("teacher")

  print(f"DEBUG: Retrieved Availability - {list(available_slots.values())}")

  # Convert queryset to dictionary for quick lookup
  booking_dict = {}

  for slot in available_slots:
    date_key = slot.date.strftime('%Y-%m-%d')
    time_key = slot.start_time.strftime('%H:%M:%S')

    if date_key not in booking_dict:
      booking_dict[date_key] = {}

    if time_key not in booking_dict[date_key]:
      booking_dict[date_key][time_key] = []

    booking_dict[date_key][time_key].append(slot.teacher)

  print(f"DEBUG: Final Booking Dictionary - {booking_dict}")

  # Ensure all slots exist, defaulting to an empty list (`[]`) if no teacher is available
  for day in week_dates:
    day_str = day.strftime('%Y-%m-%d')
    if day_str not in booking_dict:
      booking_dict[day_str] = {}

    for start_time, _ in time_slots:
      time_str = start_time.strftime('%H:%M:%S')
      if time_str not in booking_dict[day_str]:
        booking_dict[day_str][time_str] = []  # Default to empty list

  # Prepare context for rendering the template
  context = {
    "today": today,
    "week_dates": week_dates,
    "time_slots": time_slots,
    "booking_dict": booking_dict,  # Pass available teachers per slot
    "current_month": calendar.month_name[start_date.month],
    "current_year": start_date.year,
    "prev_week": selected_week - 1,
    "next_week": selected_week + 1,
  }

  return render(request, "booking/student_booking_view.html", context)




