# languagelink/settings/prod.py
from .base import *
import os

DEBUG = False

# Require a real secret key in prod
if not os.getenv("SECRET_KEY") or SECRET_KEY.startswith("dev-"):
    raise RuntimeError("SECRET_KEY must be set in production")

# MUST be set (comma-separated) e.g. "languagelink.youruni.ac.uk"
ALLOWED_HOSTS = [h for h in os.getenv("ALLOWED_HOSTS","").split(",") if h]

# MariaDB/MySQL (env-driven)
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': os.getenv('DB_NAME', ''),
    'USER': os.getenv('DB_USER', ''),
    'PASSWORD': os.getenv('DB_PASSWORD', ''),
    'HOST': os.getenv('DB_HOST', '127.0.0.1'),
    'PORT': os.getenv('DB_PORT', '3306'),
    'OPTIONS': {
      'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
      'charset': 'utf8mb4',
    },
  }
}

# Real email in prod
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Security hardening (turn on when you have HTTPS)
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "true").lower() == "true"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = "same-origin"
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # if behind a proxy (nginx)
