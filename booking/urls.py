# booking/urls.py
from django.urls import path
from .views import (
  teacher_availability_view,
  toggle_availability,
  student_booking_view,
  get_available_slots,
  create_booking,
  student_bookings_list,
  teacher_bookings_list,
  admin_bookings_list,
)

urlpatterns = [
  path("availability/", teacher_availability_view, name="teacher_availability"),
  path("toggle-availability/", toggle_availability, name="toggle_availability"),
  path("bookings/", student_booking_view, name="student_booking_view"),
  path("get-available-slots/", get_available_slots, name="get_available_slots"),
  path('booking/create/', create_booking, name='create_booking'),
  path("student/bookings/", student_bookings_list, name="student_bookings_list"),
  path("teacher/bookings/", teacher_bookings_list, name="teacher_bookings_list"),
  path("admin/bookings/", admin_bookings_list, name="admin_bookings_list"),
]
