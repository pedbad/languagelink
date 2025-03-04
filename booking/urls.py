from django.urls import path
from .views import teacher_availability_view

urlpatterns = [
    path("availability/", teacher_availability_view, name="teacher_availability"),
]
