from django.urls import path
from .views import teacher_availability_view, toggle_availability

urlpatterns = [
    path("availability/", teacher_availability_view, name="teacher_availability"),
    path("toggle-availability/", toggle_availability, name="toggle_availability"),
]
