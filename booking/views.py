from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta, date
import calendar
from .models import TeacherAvailability

@login_required
def teacher_availability_view(request):
  """
  Displays a month's worth of time slots for teachers to toggle their availability.
  Teachers can navigate between months.
  """
  if request.user.role != 'teacher':
    return redirect('teacher_profile')  # Only teachers can access this page

  # Get current year and month from query params (or use today's date)
  year = int(request.GET.get('year', datetime.today().year))
  month = int(request.GET.get('month', datetime.today().month))

  # Ensure month is always between 1-12
  if month < 1 or month > 12:
    month = datetime.today().month  # Fallback to current month

  # Debug: Print the resolved month name in console
  print(f"DEBUG: Resolved month - {calendar.month_name[month]} ({month})")

  # Get number of days in the month
  _, num_days = calendar.monthrange(year, month)
  
  # Generate dates for the entire month
  #month_dates = [date(year, month, day) for day in range(1, num_days + 1)]
  
  # Generate dates for the entire month, but exclude Saturdays (5) and Sundays (6)
  month_dates = [date(year, month, day) for day in range(1, num_days + 1) if date(year, month, day).weekday() < 5]


  # Define 30-minute time slots from 9:00 AM to 5:30 PM
  time_slots = [
    (datetime(year=2000, month=1, day=1, hour=hour, minute=minute).time(),
    (datetime(year=2000, month=1, day=1, hour=hour, minute=minute) + timedelta(minutes=30)).time())
    for hour in range(9, 18) for minute in (0, 30)  # Change 17 → 18 to include 5:30 PM
  ]


  # Fetch the teacher's availability for the month
  teacher_availabilities = TeacherAvailability.objects.filter(
    teacher=request.user, date__year=year, date__month=month
  )

  # Convert availability into a dictionary for quick lookup
  availability_dict = {
    (slot.date, slot.start_time): slot.is_available
    for slot in teacher_availabilities
  }

  context = {
    "today": date.today(),
    "month_dates": month_dates,
    "time_slots": time_slots,
    "availability_dict": availability_dict,
    "current_month": calendar.month_name[month],  # Ensure month name is correctly passed
    "current_year": year,
    "prev_month": (month - 1) if month > 1 else 12,
    "prev_year": year if month > 1 else year - 1,
    "next_month": (month + 1) if month < 12 else 1,
    "next_year": year if month < 12 else year + 1,
  }

  return render(request, "booking/teacher_availability.html", context)
