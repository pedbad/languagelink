# languagelink/settings/dev.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]  # or limit to localhost

# DB stays SQLite from base.py
