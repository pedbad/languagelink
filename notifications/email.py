# notifications/email.py
# Minimal email helper used by notifications.
# Keeps sending logic in one place so we can extend later (HTML, templates, etc.)
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def send_plain_email(subject, to, body_text, bcc=None, reply_to=None):
  """
  Send a simple plain-text email.
  - subject: string
  - to: list[str] of recipient emails
  - body_text: plain text body
  - bcc: optional list[str]
  - reply_to: optional list[str]
  """
  msg = EmailMultiAlternatives(
    subject=subject,
    body=body_text,
    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
    to=to,
    bcc=bcc or [],
    reply_to=reply_to or [],
  )
  msg.send()
