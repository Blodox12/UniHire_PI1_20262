# UniHire (Django Edition)

*Helping university students find their first professional opportunities through skill-based job matching.*

This project was migrated from a React (Vite) frontend + Django REST/Flask API
into a single, server-rendered **Django** application. There is no JavaScript
framework, no Node.js, and no separate API layer — every page is rendered with
Django templates and plain HTML/CSS, and all business logic lives in Django
views backed by the Django ORM.

## Technology

- Python 3.10+ / Django (see `requirements.txt`)
- SQLite database
- Server-side session authentication (replaces the previous JWT + localStorage flow)
- Plain HTML templates + a single CSS file (no build step, no JS framework)

## Features (ported 1:1 from the original app)

- Student and Company registration and login (role based)
- Student profile management (university, career, semester, skills, certifications, resume filename)
- Job posting management for companies (create, edit, delete)
- Job search and filtering (keyword, job type, location)
- Job recommendations for students based on skill overlap with job requirements
- Applying to jobs and tracking application status (Pending / Accepted / Rejected)
- Company view of applicants per job posting, with status updates
- Django admin panel for all models (Student, Company, Job, Application)

## Local Execution

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open `http://localhost:8000/`.

## Running Tests

```bash
python manage.py test core
```

The test suite covers registration, login, job search/filtering, job CRUD,
applying to jobs, recommendations, applicant status updates, and access
control on protected pages — equivalent to the coverage of the original
`test_api.py` suite.

## Project Structure

```
UniHire_PI1_20262-main/
├── manage.py
├── requirements.txt
├── unihire/            Django project (settings, urls, wsgi/asgi)
└── core/                Single app with all functionality
    ├── models.py         Student, Company, Job, Application
    ├── forms.py           Validation rules (email format, password length, semester range)
    ├── views.py            All page logic + session-based auth
    ├── urls.py
    ├── admin.py
    ├── templates/core/    HTML templates (one per page)
    └── migrations/
static/css/style.css      Single stylesheet (ported from the original design)
```

## Notes on the migration

- Authentication now uses Django sessions instead of JWT tokens stored in
  `localStorage`. Passwords are hashed with Django's built-in password hasher.
- The React SPA's client-side tabs (role switch on login/register, dashboard
  sections) became plain links with query parameters (`?view=...`,
  `?role=...`), so the same navigation works with zero JavaScript.
- The visual design (colors, spacing, cards, badges, navbar, dashboard
  layout) was ported directly from the original `index.css` / `App.css` into
  `static/css/style.css`, keeping the same class names where practical.
- The React frontend, the old Flask backend, and the Django REST API layer
  were removed entirely; this is now the only backend/frontend for the app.
