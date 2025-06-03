from django.contrib import admin
from .models import TeacherAvailability, Booking

@admin.register(TeacherAvailability)
class TeacherAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'date', 'start_time', 'end_time', 'is_available')
    list_filter = ('date', 'is_available')
    search_fields = ('teacher__user__first_name', 'teacher__user__last_name')

    def teacher(self, obj):
        return obj.teacher.get_full_name()  # Display teacher's full name


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'teacher', 'date', 'start_time', 'end_time', 'booked_at', 'short_message'
    )
    list_filter = ('teacher_availability__date',)
    search_fields = (
        'student__first_name', 'student__last_name',
        'teacher_availability__teacher__first_name',
        'teacher_availability__teacher__last_name',
        'message'
    )

    def teacher(self, obj):
        return obj.teacher_availability.teacher.get_full_name()

    def date(self, obj):
        return obj.teacher_availability.date

    def start_time(self, obj):
        return obj.teacher_availability.start_time

    def end_time(self, obj):
        return obj.teacher_availability.end_time

    def short_message(self, obj):
        return obj.message[:40] + '…' if obj.message and len(obj.message) > 40 else (obj.message or "—")
    short_message.short_description = "Message"
