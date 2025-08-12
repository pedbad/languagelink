# booking/utils.py
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone

def slot_is_in_past_or_too_soon(slot_date, slot_start_time, *, lead_minutes=None):
  """
  A tiny utility that answers: “Is this slot in the past, or too soon (within BOOKING_LEAD_MINUTES)?
  True if the slot starts in the past OR within lead_minutes from 'now'
  (using the project's timezone).
  - slot_date: datetime.date
  - slot_start_time: datetime.time
  """
  # default to settings, but allow an override for tests
  lead = settings.BOOKING_LEAD_MINUTES if lead_minutes is None else int(lead_minutes)

  # 'now' in local (Europe/London) time
  now_local = timezone.localtime()

  # build an aware datetime for the slot start in the current TZ
  slot_start_naive = datetime.combine(slot_date, slot_start_time)
  slot_start = timezone.make_aware(slot_start_naive, timezone.get_current_timezone())

  cutoff = now_local + timedelta(minutes=lead)
  return slot_start <= cutoff
