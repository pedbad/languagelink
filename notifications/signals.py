# notifications/signals.py
# Signal receivers that trigger notifications.

from django.db.models.signals import post_save
from django.dispatch import receiver

from booking.models import Booking
from .services import notify_booking_created


@receiver(post_save, sender=Booking)
def _notify_on_booking_created(sender, instance: Booking, created: bool, raw: bool, **kwargs):
  """
  When a new Booking row is created, notify:
    - student (confirmation)
    - teacher (new booking)
    - admins (copy)
  Notes:
    - `raw` is True during loaddata/fixtures; skip to avoid duplicate sends.
  """
  if raw:
    return
  if created:
    notify_booking_created(instance)
