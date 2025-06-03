from django.db import models
from django.conf import settings
from datetime import time

class TeacherAvailability(models.Model):
    """
    Stores the available time slots for each teacher.
    Teachers can manually select which slots they are available for.
    """
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="availability")
    date = models.DateField()
    
    # Time slot field, each slot represents a 30-minute period
    start_time = models.TimeField()
    end_time = models.TimeField()

    is_available = models.BooleanField(default=False)  # Teachers must manually mark slots as available

    class Meta:
        unique_together = ('teacher', 'date', 'start_time')  # Prevent duplicate availability entries
        ordering = ['date', 'start_time']  # Order slots chronologically

    def __str__(self):
        return f"{self.teacher.email} - {self.date} ({self.start_time} - {self.end_time})"


class Booking(models.Model):
    """
    Stores which students have booked which time slots.
    Ensures that once a slot is booked, it cannot be booked by another student.
    """
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    teacher_availability = models.OneToOneField(TeacherAvailability, on_delete=models.CASCADE, related_name="booking")
    booked_at = models.DateTimeField(auto_now_add=True)

    # Optional short message from student (max 300 characters)
    message = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text="Optional message from student when booking this slot."
    )

    class Meta:
        ordering = ['teacher_availability__date', 'teacher_availability__start_time']

    def __str__(self):
        return f"{self.student.email} booked {self.teacher_availability}"

