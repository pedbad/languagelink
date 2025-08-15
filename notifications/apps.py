# notifications/apps.py
from django.apps import AppConfig

class NotificationsConfig(AppConfig):
  default_auto_field = 'django.db.models.BigAutoField'
  name = 'notifications'

  def ready(self):
    import notifications.signals  # noqa: F401 # Import the signals module when the app is ready

    
