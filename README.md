# 🏫 LanguageLink Advising System

**LanguageLink** is a web-based application that facilitates scheduling and managing language advising appointments between students and teachers. It’s built with **Django** for the backend (and optionally TailwindCSS for styling).

---

# Local Dev (SQLite & MySQL) — Step-by-Step

This guide shows **two local setups** side-by-side:

- **Dev (SQLite)** — simplest path, no DB server
- **Dev (MySQL)** — mirrors production-style DB locally (via Homebrew)

Each section includes quick **sanity checks** so you always know what worked.

---

## 0) Prerequisites

- **Python 3.12.10** (currently used)
- **pip** & **venv** (bundled with Python)
- **Git**
- **Node.js** (optional; only needed if you’ll build Tailwind assets)
- **Homebrew** (macOS) if you’ll run MySQL locally: <https://brew.sh>

> On Apple Silicon, Homebrew lives at `/opt/homebrew`.

---

## 🚀 Installation & Setup

## 1) Clone the repo

### **1️⃣ Clone the Repository**
If you haven’t already, clone the repository:
```bash
git clone https://github.com/your-repo/languagelink.git
cd languagelink
```

Your tree should look roughly like:

```
advising-team/
├─ manage.py
├─ languagelink/
│  ├─ settings/
│  │  ├─ __init__.py
│  │  ├─ base.py
│  │  ├─ dev.py
│  │  ├─ dev_mysql.py
│  │  └─ prod.py
│  └─ urls.py
├─ core/, users/, booking/, notifications/ ...
└─ requirements/
   ├─ base.txt
   ├─ dev.txt
   ├─ dev-mysql.txt
   └─ prod.txt
```


---

## 2) Environment files

### 2.1 `.env` (local, not committed)

Create `./.env` at the repo root (same folder as `manage.py`). Example for **SQLite dev**:

```dotenv
# Core
DJANGO_SETTINGS_MODULE=languagelink.settings.dev
SECRET_KEY=dev-only-not-for-prod
DEBUG=true
SITE_URL=http://localhost:8000
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Email (safe dev backends)
EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
EMAIL_FILE_PATH=./tmp_emails
DEFAULT_FROM_EMAIL=LanguageLink <no-reply@langcen.cam.ac.uk>
EMAIL_SUBJECT_PREFIX=[LanguageLink]

# Booking
BOOKING_LEAD_MINUTES=60
TIME_ZONE=Europe/London
```

> **Do not commit** your real `.env`. Keep `.env` in `.gitignore` (it already should be).

### 2.2 Production examples

- `./.env.example` — safe **dev** template (no secrets)
- `./.env.prod.example` — **prod** template (no secrets, comments on what to set)

Collaborators copy these to their own `.env`.


---

## 3) Virtual environments (two local venvs)
We keep two venvs to avoid mixing SQLite-only and MySQL dependencies:
Inside each venv, verify what Django will run with, eg: 

.venv — SQLite dev
.venv-mysql — MySQL dev

```bash
python -c "import sys; print(sys.version)"
python -V
which python
```

If you want to align both venvs preferred:
```bash
pyenv install 3.12.10   # or 3.13.7
pyenv local 3.12.10     # sets version in this repo
python -m venv .venv    # recreate venvs as needed
```

Or just recreate the specific venv using the desired interpreter:
```bash
/path/to/python3.12 -m venv .venv-sqlite
/path/to/python3.12 -m venv .venv-mysql
```

We’ll make **two** venvs to keep dependencies clean:

- `.venv` — **SQLite** dev
- `.venv-mysql` — **MySQL** dev

### 3.1 SQLite venv

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
# (dev.txt usually includes: "-r base.txt" and optional dev tools)
```

Sanity check:

```bash
python -c "import django; print('Django', django.get_version())"
```

### 3.2 MySQL venv

```bash
python -m venv .venv-mysql
source .venv-mysql/bin/activate
pip install -r requirements/dev-mysql.txt
```

Sanity check the MySQL driver:

```bash
python - <<'PY'
import MySQLdb
from MySQLdb import _mysql
print("mysqlclient import OK")
print("client library:", _mysql.get_client_info())
print("module path:", MySQLdb.__file__)
print("version_info (module):", getattr(MySQLdb, "version_info", "n/a"))
PY
```


---

## 4) Running with **SQLite** (the easy path)

1) Ensure your `.env` points to the **dev** settings:

```dotenv
DJANGO_SETTINGS_MODULE=languagelink.settings.dev
```

2) Activate the **SQLite** venv and migrate:

```bash
source .venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
```

3) Run the server:

```bash
python manage.py runserver
```

4) Visit <http://127.0.0.1:8000> and sign in with the superuser you just created.


---

## 5) Running with **MySQL** locally (mirrors prod DB)

### 5.1 Install MySQL (Homebrew)

Check if present:

```bash
mysql --version || echo "MySQL not installed"
```

If needed, install and start:

```bash
brew update
brew install mysql
brew services start mysql
```

Confirm it’s up (look for a running mysqld and socket path):

```bash
brew services list | grep mysql
tail -n 50 /opt/homebrew/var/mysql/*.err
```

> Homebrew MySQL listens on TCP **and** creates a UNIX socket (usually `/tmp/mysql.sock`).

### 5.2 Prepare MySQL root access (first time only)
If root has no password, harden it!
If root has no password (Homebrew default), run the MySQL hardening script:

```bash
mysql_secure_installation
```

Set a **local dev** root password (e.g. `LocalDevPassword`).

### 5.3 Create DB + user for the app

Connect as root using the UNIX socket (replace the password prompt as needed):

```bash
mysql -u root -p --protocol=SOCKET --socket=/tmp/mysql.sock <<'SQL'
-- Create DB (MariaDB‑friendly collation)
CREATE DATABASE IF NOT EXISTS languagelink_dev
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- (Re)create app user with a local‑dev password
DROP USER IF EXISTS 'languagelink_user'@'localhost';
CREATE USER 'languagelink_user'@'localhost'
  IDENTIFIED BY 'DevOnly_StrongPassword!';

GRANT ALL PRIVILEGES ON languagelink_dev.* TO 'languagelink_user'@'localhost';
FLUSH PRIVILEGES;
SQL
```

Sanity check the user can connect via the socket and sees the DB:

```bash
mysql -u languagelink_user -p \
  --protocol=SOCKET --socket=/tmp/mysql.sock \
  -D languagelink_dev \
  -e "SELECT DATABASE() AS using_db, CURRENT_USER() AS curr_user, @@version AS mysql_version, @@socket AS sock;"
```

Expected output contains:

```
using_db         | curr_user                   | mysql_version | sock
languagelink_dev | languagelink_user@localhost | 9.x.x         | /tmp/mysql.sock
```

### 5.4 Configure Django to use MySQL locally
Point Django at MySQL settings

Use **dev_mysql** settings. Either export in your shell or add to `.env`:

```bash
# in your shell for a single session:
export DJANGO_SETTINGS_MODULE=languagelink.settings.dev_mysql
# or in .env (persistent):
DJANGO_SETTINGS_MODULE=languagelink.settings.dev_mysql
```

`languagelink/settings/dev_mysql.py` should look like this (summary):

```python
from .base import *
DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "languagelink_dev"),
        "USER": os.getenv("DB_USER", "languagelink_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),  # empty => prefer unix socket
        "PORT": int(os.getenv("DB_PORT", "3306")),
        "OPTIONS": {
            "charset": "utf8mb4",
            "unix_socket": os.getenv("DB_SOCKET", "/tmp/mysql.sock"),
            "init_command": "SET sql_require_primary_key=OFF",
        },
    }
}
```

Also set these **in `.env`** (only needed for MySQL dev):

```dotenv
DB_NAME=languagelink_dev
DB_USER=languagelink_user
DB_PASSWORD=DevOnly_StrongPassword!
DB_PORT=3306
DB_SOCKET=/tmp/mysql.sock
```

### 5.5 Migrate and run (MySQL)

Use the **MySQL venv**:

```bash
source .venv-mysql/bin/activate

# sanity (see which settings are active)
python manage.py diffsettings | egrep 'DATABASES|ENGINE|NAME|HOST|PORT' -A2

# migrate
python manage.py migrate

# create an admin user for this DB
python manage.py createsuperuser

# run
python manage.py runserver
```

### 5.6 Verify tables exist in MySQL

After migrating, check tables:

```bash
mysql -u languagelink_user -p \
  --protocol=SOCKET --socket=/tmp/mysql.sock \
  -D languagelink_dev -e "SHOW TABLES;"
```


---

## 6) Switching between SQLite and MySQL

- **SQLite run:**  
  ```bash
  # terminal A
  source .venv/bin/activate
  export DJANGO_SETTINGS_MODULE=languagelink.settings.dev
  python manage.py runserver
  ```

- **MySQL run:**  
  ```bash
  # terminal B
  source .venv-mysql/bin/activate
  export DJANGO_SETTINGS_MODULE=languagelink.settings.dev_mysql
  python manage.py runserver
  ```

> Keep the two venvs separate to avoid installing `mysqlclient` where it isn’t needed.


---

## 7) Emails in dev

By default in dev we use **file‑based** emails so nothing leaves your machine:

- Backend: `django.core.mail.backends.filebased.EmailBackend`
- Folder: `./tmp_emails`

Open the generated `.eml` files in any mail client for testing.


---

## 8) (Optional) Makefile shortcuts
f Makefile is present in the repo root, you can use these shortcuts.
If you added the example `Makefile`, you can run:

8.1 Cheatsheet
SQLite dev

```bash
ake run                 # runserver with languagelink.settings.dev
make migrate             # apply migrations (dev DB)
make makemigrations      # generate migrations
make shell               # Django shell with dev settings
make createsuperuser     # create admin in dev DB
make check               # Django system checks
make diffsettings        # show effective settings (dev)
make test                # run tests (dev)
```

MySQL dev
```bash
make run-mysql
make migrate-mysql
make shell-mysql
make createsuperuser-mysql
make diffsettings-mysql
```

Prod settings (run locally with your current .env)
```bash
make run-prod-local      # runserver 0.0.0.0:8000 with prod settings
make migrate-prod
make collectstatic-prod
make shell-prod
make createsuperuser-prod
make test-prod
```
In Makefile use a help target, you can list targets:
```bash
make help
```
> If a Make command fails, fall back to the explicit Python commands shown above.


---

## 9) Tailwind / Node (optional)  npm --version 11.4.2

If you’re working on styling and Tailwind:

```bash
# once
npm install

# dev
npm run watch

# production build (minified)
npm run build
```


---

## 10) Common pitfalls & fixes

- **`OperationalError: (1227) ... privilege ...` during `migrate`**  
  Make sure your MySQL user has privileges on the DB:  
  `GRANT ALL PRIVILEGES ON languagelink_dev.* TO 'languagelink_user'@'localhost';`  
  Then `FLUSH PRIVILEGES;`. Re-run `migrate`.

- **Socket vs TCP confusion**  
  This guide uses the UNIX socket at `/tmp/mysql.sock`. Keep `HOST` empty in Django and set `DB_SOCKET=/tmp/mysql.sock`. If you *prefer* TCP, set `HOST=127.0.0.1` (or `localhost`) and omit the `unix_socket` option.

- **Wrong settings module**  
  Use `python manage.py diffsettings | head -n 20` to confirm which settings are active.


---

## 11) Production notes (very brief)

- Use `languagelink.settings.prod` with `DEBUG=false`
- Strong `SECRET_KEY` from env
- Real SMTP (university mail server)
- MySQL/MariaDB with utf8mb4
- Collect static with `python manage.py collectstatic`
- Serve static via your web server (or WhiteNoise if desired)

> See `.env.prod.example` for all required values and comments.


---

## 12) Quick reference

- **SQLite dev run (fastest):**
  ```bash
  source .venv/bin/activate
  export DJANGO_SETTINGS_MODULE=languagelink.settings.dev
  python manage.py migrate
  python manage.py runserver
  ```

- **MySQL dev run (prod‑like):**
  ```bash
  source .venv-mysql/bin/activate
  export DJANGO_SETTINGS_MODULE=languagelink.settings.dev_mysql
  python manage.py migrate
  python manage.py runserver
  ```

Happy hacking! 🎉
