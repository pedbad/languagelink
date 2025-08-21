# Makefile for LanguageLink
# -------------------------------------------------------------------
# Quick usage (uses your current Python unless you override PY=...):
#   make                     # show this help
#   make run                 # dev (SQLite) server
#   make migrate             # dev (SQLite) migrations
#   make run-mysql PY=.venv-mysql/bin/python   # dev (MySQL) server
#   make migrate-mysql PY=.venv-mysql/bin/python
#   make run-prod-local      # run with prod settings locally
#
# Tip: You can pass a different interpreter per call:
#   make run PY=.venv/bin/python
# -------------------------------------------------------------------

# ----- Variables ----------------------------------------------------
PY ?= python                          # override per call: make run PY=.venv/bin/python
MANAGE := $(PY) manage.py

# Explicit settings modules
DJANGO_DEV   := DJANGO_SETTINGS_MODULE=languagelink.settings.dev
DJANGO_MYSQL := DJANGO_SETTINGS_MODULE=languagelink.settings.dev_mysql
DJANGO_PROD  := DJANGO_SETTINGS_MODULE=languagelink.settings.prod

# Default goal (so 'make' shows help)
.DEFAULT_GOAL := help

# ----- Helpers ------------------------------------------------------
.PHONY: help \
        run migrate makemigrations shell createsuperuser check diffsettings test \
        run-mysql migrate-mysql shell-mysql diffsettings-mysql createsuperuser-mysql \
        run-prod-local migrate-prod collectstatic-prod shell-prod createsuperuser-prod test-prod

help: ## Show this help and available targets
	@echo "LanguageLink — Make targets"; \
	awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_.-]+:.*##/ \
	{ printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# ----- Development (SQLite) ----------------------------------------
run: ## Run dev server (SQLite) with settings.dev
	$(DJANGO_DEV) $(MANAGE) runserver

migrate: ## Apply migrations (SQLite)
	$(DJANGO_DEV) $(MANAGE) migrate

makemigrations: ## Create new migrations from model changes (SQLite)
	$(DJANGO_DEV) $(MANAGE) makemigrations

shell: ## Open Django shell (SQLite)
	$(DJANGO_DEV) $(MANAGE) shell

createsuperuser: ## Create a superuser in the SQLite DB
	$(DJANGO_DEV) $(MANAGE) createsuperuser

check: ## Django system checks (SQLite)
	$(DJANGO_DEV) $(MANAGE) check

diffsettings: ## Show effective settings diff (SQLite)
	$(DJANGO_DEV) $(MANAGE) diffsettings

test: ## Run tests (SQLite)
	$(DJANGO_DEV) $(MANAGE) test

# ----- Development (MySQL) -----------------------------------------
run-mysql: ## Run dev server (MySQL) with settings.dev_mysql
	$(DJANGO_MYSQL) $(MANAGE) runserver

migrate-mysql: ## Apply migrations (MySQL)
	$(DJANGO_MYSQL) $(MANAGE) migrate

shell-mysql: ## Open Django shell (MySQL)
	$(DJANGO_MYSQL) $(MANAGE) shell

diffsettings-mysql: ## Show effective settings diff (MySQL)
	$(DJANGO_MYSQL) $(MANAGE) diffsettings

createsuperuser-mysql: ## Create a superuser in the MySQL DB
	$(DJANGO_MYSQL) $(MANAGE) createsuperuser

# ----- Production-mode (local) -------------------------------------
# Handy to smoke-test prod settings on your machine using your local .env
run-prod-local: ## Run server with settings.prod on 0.0.0.0:8000
	$(DJANGO_PROD) $(MANAGE) runserver 0.0.0.0:8000

migrate-prod: ## Apply migrations with settings.prod
	$(DJANGO_PROD) $(MANAGE) migrate

collectstatic-prod: ## Collect static files for prod
	$(DJANGO_PROD) $(MANAGE) collectstatic --noinput

shell-prod: ## Open Django shell with settings.prod
	$(DJANGO_PROD) $(MANAGE) shell

createsuperuser-prod: ## Create a superuser in the prod DB (be careful!)
	$(DJANGO_PROD) $(MANAGE) createsuperuser

test-prod: ## Run tests with settings.prod
	$(DJANGO_PROD) $(MANAGE) test

# -------------------------------------------------------------------
# README-style notes (comments only; safe to leave in this file)
#
# DEV (SQLite)
#  1) Ensure your .env has: DJANGO_SETTINGS_MODULE=languagelink.settings.dev
#  2) Activate venv: source .venv/bin/activate
#  3) Run: make migrate
#  4) Run: make createsuperuser
#  5) Run: make run
#
# DEV (MySQL)
#  1) Ensure your .env has: DJANGO_SETTINGS_MODULE=languagelink.settings.dev_mysql
#     and DB_* values (DB_NAME, DB_USER, DB_PASSWORD, DB_SOCKET=/tmp/mysql.sock)
#  2) Use the MySQL venv per call by overriding PY:
#       make migrate-mysql  PY=.venv-mysql/bin/python
#       make createsuperuser-mysql PY=.venv-mysql/bin/python
#       make run-mysql      PY=.venv-mysql/bin/python
#
# PROD (local smoke test)
#  1) Prepare a local .env with prod-like values (never commit secrets)
#  2) Run: make run-prod-local
#
# TABS vs SPACES
#  • Every command line under a target must start with a real TAB.
#    If you see “missing separator” errors, replace leading spaces with a TAB.
#
# Override Python interpreter per-call (examples)
#  • make run PY=.venv/bin/python
#  • make run-mysql PY=.venv-mysql/bin/python
# -------------------------------------------------------------------
