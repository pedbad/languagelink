'''
Run it locally with :
DJANGO_SETTINGS_MODULE=languagelink.settings.dev_mysql python manage.py runserver

'''

from .base import *
DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "languagelink_dev"),
        "USER": os.getenv("DB_USER", "languagelink_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        # Leave HOST empty to prefer the unix socket below
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": int(os.getenv("DB_PORT", "3306")),
        "OPTIONS": {
            "charset": "utf8mb4",
            # Homebrew’s default socket:
            "unix_socket": os.getenv("DB_SOCKET", "/tmp/mysql.sock"),
            # Helpful for dev to avoid hard failures on missing PKs during quick iterations
        },
    }
}
