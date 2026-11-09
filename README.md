# UniHire 

*Helping university students find their first professional opportunities through skill-based job matching.*

UniHire is a server-rendered **Django** application. — every page is rendered
with Django templates and plain HTML/CSS, and all business logic lives in
Django views backed by the Django ORM.

The project is organized into three focused Django apps, each responsible
for a single area of the product: `core` (public pages and shared layout),
`accounts` (users and authentication), and `jobs` (job postings and
applications).

## Technology

- Python 3.10+ / Django (see `requirements.txt`)
- SQLite database
- Server-side session authentication with Django's auth system
- Hashed password storage via Django's `set_password()` / `authenticate()` workflow
- Automatic login after successful student or company registration
- Plain HTML templates + a single CSS file (no build step, no JS framework)
- Supported browsers: latest versions of Chrome, Firefox, Edge and Safari. The
  stylesheet includes `-webkit-` prefixes for Safari and fallbacks for browsers
  without `backdrop-filter` or `min()`.

## Features

- Student and Company registration and login (role based)
- Django-backed user accounts with hashed passwords and role-specific authentication
- Automatic session login after a successful student or company registration
- Student profile management (university, career, semester, skills, certifications, resume filename)
- Job posting management for companies (create, edit, delete)
- Job search and filtering (keyword, job type, location)
- Job recommendations for students based on skill overlap with job requirements
- Applying to jobs and tracking application status (Pending / Accepted / Rejected)
- Company view of applicants per job posting, with status updates
- Django admin panel for all models (Student, Company, Job, Application)
- Account deletion from the profile page (password required): removes the
  user, profile, uploaded files, job postings and applications. Other advanced
  privacy compliance features are out of the MVP scope.

## Getting Started

These steps work on any operating system and don't require any prior Django
experience — just Python installed on your machine.

### 1. Prerequisites

- **Python 3.10 or higher**. Check your version with:
  ```bash
  python --version
  ```
  (On some systems, use `python3` instead of `python`.) If you don't have
  Python installed, download it from [python.org](https://www.python.org/downloads/).
- **Git**, to download the project. Check with:
  ```bash
  git --version
  ```
  If you don't have it, download it from [git-scm.com](https://git-scm.com/downloads).

### 2. Download the project

Clone the repository to your computer:

```bash
git clone https://github.com/Blodox12/UniHire_PI1_20262.git
cd UniHire_PI1_20262
```

(Replace the URL with your own repository's URL if you're working from a
fork.) You can also download it as a ZIP from GitHub's green "Code" button
and extract it, if you'd rather not use Git.


### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up the database

This creates the local SQLite database file and its tables:

```bash
python manage.py migrate
```

When the project evolves and a custom Django user model or profile relationship is added, the migrations must be applied in order. If you encounter a stale or inconsistent local SQLite state, delete the existing `db.sqlite3` file and run the migration command again to recreate the database cleanly.


### 5. Run the project

```bash
python manage.py runserver
```

Open your browser at **http://localhost:8000/**. You should see the UniHire
home page. Press `Ctrl+C` in the terminal to stop the server when you're
done.


## Project Structure

The code is split into three Django apps. Each app owns its models, forms,
views, URLs, templates and tests, and apps only talk to each other through
models and the helpers in `accounts/utils.py` and `accounts/decorators.py`.

```
UniHire_PI1_20262/
├── manage.py
├── requirements.txt
├── .env.example             Environment variables (copy to .env)
├── unihire/                 Django project (settings, urls, wsgi/asgi)
├── core/                    Public pages, shared layout and site-wide utilities
│   ├── views.py               home, about, health check
│   ├── models.py              Testimonial
│   ├── context_processors.py  session_user (exposes session info to all templates)
│   ├── templates/             403/404/500 pages, core/base.html (shared layout),
│   │                          core/home.html, core/about.html
│   └── urls.py
├── accounts/                Users, authentication and profiles
│   ├── models.py              CustomUser, Student, StudentDocument, Company
│   ├── forms.py               Registration, login and profile forms
│   ├── views.py               Login, logout, registration, profiles
│   ├── decorators.py          login_required(role=...), approved_company_required
│   ├── utils.py               current_student(request), current_company(request)
│   ├── admin.py               Includes company approval actions
│   ├── templates/accounts/    Login, registration, profile and password reset pages
│   ├── tests.py
│   └── urls.py
├── jobs/                    Job postings and applications
│   ├── models.py              Job, Application
│   ├── forms.py               JobForm, ResumeForm
│   ├── views.py               Job search/detail/CRUD, dashboards, applications
│   ├── admin.py
│   ├── templates/jobs/        Job list/detail/form, dashboards and partials (_*.html)
│   ├── tests.py
│   └── urls.py
└── static/                  css/style.css (single stylesheet) and img/
```

## Development conventions

- **Where code goes:** put new features in the app that owns the data. Shared
  layout goes in `core/templates/core/base.html`; reusable template fragments
  are partials named `_name.html`.
- **Views stay thin:** validation lives in forms, rules about a single record
  live in model methods (for example `Application.decide()`).
- **Configuration:** never hard-code secrets or environment-specific values;
  read them from `.env` in `unihire/settings.py` and list them in `.env.example`.
- **Database changes:** after editing a model, run
  `python manage.py makemigrations` and commit the migration with the change.
- **Before pushing:** run `python manage.py check` and `python manage.py test`.
- **Git:** one feature branch per change (`feature/<name>`), merged to `main`
  through a pull request. Reference the issue in the commit message, e.g.
  `NFR-06: ... (#19)`.
- **Formatting:** follow `.editorconfig` (4 spaces in Python, 2 in HTML/CSS).




## Operations

### Availability and health check

`GET /health/` returns `{"status": "ok", "database": "ok"}` with HTTP 200 when
the app can reach its database, and HTTP 503 otherwise. Point an uptime monitor
(for example UptimeRobot) or your hosting platform's health check at this URL
so downtime is detected and alerted on. The 99 % availability target also
depends on the hosting provider; schedule maintenance windows outside peak
hours.

### Scalability (SQLite)

The project uses SQLite by requirement. To support around 200 concurrent
users, `unihire/settings.py` enables WAL mode (reads don't block while a
request writes), `IMMEDIATE` transactions and a 20-second lock timeout, and
keeps sessions in a cache backed by the database. Job search is paginated and
the filtered fields are indexed.

In production, run Django behind a multi-threaded WSGI server instead of
`runserver`, for example:

```bash
pip install waitress
waitress-serve --threads=16 --listen=0.0.0.0:8000 unihire.wsgi:application
```

SQLite allows one writer at a time, so keep the database on the same server's
local disk (not a network drive). WAL mode creates `db.sqlite3-wal` and
`db.sqlite3-shm` next to the database; they are part of it and are ignored by Git.

### Database backups

```bash
python manage.py backup_db            # creates backups/db-YYYYMMDD-HHMMSS.sqlite3
python manage.py backup_db --keep 30  # keep the last 30 copies (default: 7)
```

The command uses SQLite's backup API, so it is safe to run while the site is
in use, and it checks the copy with `PRAGMA integrity_check`. Set
`DJANGO_BACKUP_DIR` in `.env` to store copies elsewhere (ideally another
disk). Uploaded files in `media/` are not included; copy that folder too.

To run it automatically every 24 hours:

- **Windows (Task Scheduler)**, replacing the path with your project folder:
  ```powershell
  schtasks /Create /SC DAILY /ST 03:00 /TN "UniHire DB backup" /TR "cmd /c cd /d C:\path\to\UniHire_PI1_20262 && python manage.py backup_db"
  ```
- **Linux/macOS (cron)**, `crontab -e`:
  ```
  0 3 * * * cd /path/to/UniHire_PI1_20262 && python manage.py backup_db
  ```

To restore, stop the server and replace `db.sqlite3` with a backup file
(delete any `db.sqlite3-wal` / `db.sqlite3-shm` files first).

### Error logs

Errors and warnings (including unhandled exceptions behind 500 pages, failed
decision emails and missing resume files) are written to the console and to
`logs/unihire.log`. The file rotates at 5 MB and keeps 5 old copies. Set
`DJANGO_LOG_DIR` or `DJANGO_LOG_LEVEL` in `.env` to change the folder or level.
