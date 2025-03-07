# booking/urls.py
from django.urls import path
from .views import (
  teacher_availability_view,
  toggle_availability,
  student_booking_view,
  get_available_slots,
)

urlpatterns = [
  path("availability/", teacher_availability_view, name="teacher_availability"),
  path("toggle-availability/", toggle_availability, name="toggle_availability"),
  path("bookings/", student_booking_view, name="student_booking_view"),
  path("get-available-slots/", get_available_slots, name="get_available_slots"),
]
