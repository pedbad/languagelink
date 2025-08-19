# Makefile for LanguageLink
# Usage examples:
#   make run                 # dev server (settings.dev)
#   make run-prod-local      # run with settings.prod using your local .env
#   make migrate             # apply migrations (dev)
#   make migrate-prod        # apply migrations (prod)
#   make collectstatic-prod  # collect static for prod
#   make check               # Django system checks
#   make diffsettings        # see effective settings
#   make createsuperuser     # dev superuser

# ----- Variables -----
PY := python
MANAGE := $(PY) manage.py

# Explicit settings modules for commands that should override the default
DJANGO_DEV := DJANGO_SETTINGS_MODULE=languagelink.settings.dev
DJANGO_PROD := DJANGO_SETTINGS_MODULE=languagelink.settings.prod

# ----- Helpers -----
.PHONY: run run-prod-local migrate migrate-prod makemigrations \
        collectstatic-prod check diffsettings shell shell-prod \
        createsuperuser createsuperuser-prod test test-prod

# ----- Development (local) -----
run:
	$(DJANGO_DEV) $(MANAGE) runserver

migrate:
	$(DJANGO_DEV) $(MANAGE) migrate

makemigrations:
	$(DJANGO_DEV) $(MANAGE) makemigrations

shell:
	$(DJANGO_DEV) $(MANAGE) shell

createsuperuser:
	$(DJANGO_DEV) $(MANAGE) createsuperuser

check:
	$(DJANGO_DEV) $(MANAGE) check

diffsettings:
	$(DJANGO_DEV) $(MANAGE) diffsettings

test:
	$(DJANGO_DEV) $(MANAGE) test

# ----- Production-mode commands (use your current .env) -----
# These targets run Django with the prod settings module *locally*,
# which is handy for a smoke test before deploying.
run-prod-local:
	$(DJANGO_PROD) $(MANAGE) runserver 0.0.0.0:8000

migrate-prod:
	$(DJANGO_PROD) $(MANAGE) migrate

collectstatic-prod:
	$(DJANGO_PROD) $(MANAGE) collectstatic --noinput

shell-prod:
	$(DJANGO_PROD) $(MANAGE) shell

createsuperuser-prod:
	$(DJANGO_PROD) $(MANAGE) createsuperuser

test-prod:
	$(DJANGO_PROD) $(MANAGE) test
