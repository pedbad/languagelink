# languagelink/settings/base.py
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]  # /.../languagelink
load_dotenv(BASE_DIR / ".env")  # local dev convenience only

SECRET_KEY = os.getenv("SECRET_KEY", "insecure-dev-key")  # prod overrides

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Comma-separated list: "example.com,app.example.com,localhost"
ALLOWED_HOSTS = [h for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h] or ["localhost", "127.0.0.1"]

INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
    "django_ckeditor_5",
    'core','users','booking','notifications',
]

MIDDLEWARE = [
  'django.middleware.security.SecurityMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'languagelink.urls'

TEMPLATES = [{
  'BACKEND':'django.template.backends.django.DjangoTemplates',
  'DIRS': [],
  'APP_DIRS': True,
  'OPTIONS': {'context_processors':[
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
  ]},
}]

WSGI_APPLICATION = 'languagelink.wsgi.application'

# Default DB = SQLite (dev). Prod overrides in prod.py.
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',
  }
}

AUTH_PASSWORD_VALIDATORS = [
  {'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
  {'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},
  {'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},
  {'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = os.getenv("TIME_ZONE", "Europe/London")
USE_I18N = True
USE_TZ = True

# Booking rules
BOOKING_LEAD_MINUTES = int(os.getenv("BOOKING_LEAD_MINUTES", "60"))

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static', BASE_DIR / 'core/static']
STATIC_ROOT = BASE_DIR / 'staticfiles'  # used in prod collectstatic

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.CustomUser'

CKEDITOR_5_CONFIGS = {
  "default": {
    "toolbar":["bold","italic","link","bulletedList","numberedList"],
    "heading": False,
    "removePlugins":[
      "CKBox","CKFinder","EasyImage","RealTimeCollaborativeComments",
      "RealTimeCollaborativeTrackChanges","RealTimeCollaborativeRevisionHistory",
      "Comments","TrackChanges","TrackChangesData","RevisionHistory","Pagination",
      "WProofreader","MathType",
    ],
  }
}

# CSRF trusted origins (comma-separated)
_default_csrf = "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://127.0.0.1:3000"
CSRF_TRUSTED_ORIGINS = [o for o in os.getenv("CSRF_TRUSTED_ORIGINS", _default_csrf).split(",") if o]

LOGIN_URL = "/users/login/"
LOGIN_REDIRECT_URL = "/users/student/profile/"
LOGOUT_REDIRECT_URL = "/"

PASSWORD_RESET_TIMEOUT = int(os.getenv("PASSWORD_RESET_TIMEOUT", 60*60*72))

# Email
DEFAULT_FROM_EMAIL   = os.getenv("DEFAULT_FROM_EMAIL", "LanguageLink <no-reply@langcen.cam.ac.uk>")
EMAIL_SUBJECT_PREFIX = os.getenv("EMAIL_SUBJECT_PREFIX", "[LanguageLink] ")
SERVER_EMAIL         = os.getenv("SERVER_EMAIL", DEFAULT_FROM_EMAIL)

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_FILE_PATH = os.getenv("EMAIL_FILE_PATH", str(BASE_DIR / "tmp_emails"))

EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "false").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "10"))

SITE_URL = os.getenv("SITE_URL", "http://localhost:8000")
