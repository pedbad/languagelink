"""
Main URL Configuration for LanguageLink.

This file routes URLs to different Django apps:
- `core`: Handles the landing page and about section.
- `users`: Manages authentication and user profiles.
- `booking`: Handles teacher availability and student bookings.
- `admin`: Provides Django's admin interface.

Additionally, it serves media files during development.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
  # Django Admin Panel
  path('admin/', admin.site.urls),

  # Core App URLs (Landing Page & About Section)
  path('', include('core.urls')),

  # Users App URLs (Authentication, Profiles, Student/Teacher Management)
  path('users/', include('users.urls')),

  # Booking App URLs (Teacher Availability & Student Bookings)
  path('booking/', include('booking.urls')),  
    
  # ckeditor5 
  path('ckeditor5/', include('django_ckeditor_5.urls')),
]

# Serve media files during development only
if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
