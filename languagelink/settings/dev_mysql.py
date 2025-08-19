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
        "NAME": os.getenv("DB_NAME", "languagelink"),
        "USER": os.getenv("DB_USER", "languagelink_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": int(os.getenv("DB_PORT", "3306")),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
