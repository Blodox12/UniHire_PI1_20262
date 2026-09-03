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
- Server-side session authentication
- Plain HTML templates + a single CSS file (no build step, no JS framework)

## Features

- Student and Company registration and login (role based)
- Student profile management (university, career, semester, skills, certifications, resume filename)
- Job posting management for companies (create, edit, delete)
- Job search and filtering (keyword, job type, location)
- Job recommendations for students based on skill overlap with job requirements
- Applying to jobs and tracking application status (Pending / Accepted / Rejected)
- Company view of applicants per job posting, with status updates
- Django admin panel for all models (Student, Company, Job, Application)

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


### 5. Run the project

```bash
python manage.py runserver
```

Open your browser at **http://localhost:8000/**. You should see the UniHire
home page. Press `Ctrl+C` in the terminal to stop the server when you're
done.


## Project Structure

```
UniHire-Django/
├── manage.py
├── requirements.txt
├── unihire/               Django project (settings, urls, wsgi/asgi)
├── core/                  Public pages and shared layout
│   ├── views.py             home, about
│   ├── context_processors.py session_user (exposes session info to all templates)
│   ├── templates/core/      base.html (shared layout) + home.html, about.html
│   └── urls.py
├── accounts/               Users, authentication and profile
│   ├── models.py             Student, Company
│   ├── forms.py               Registration, login, profile forms
│   ├── views.py                Login, logout, registration, profile
│   ├── decorators.py           login_required(role=...)
│   ├── utils.py                 current_student(request), current_company(request)
│   ├── admin.py
│   ├── templates/accounts/     login.html, register_student.html,
│   │                            register_company.html, profile.html
│   └── urls.py
├── jobs/                    Job postings and applications
│   ├── models.py              Job, Application
│   ├── forms.py                JobForm
│   ├── views.py                 Job search/detail/CRUD, dashboards, applications
│   ├── admin.py
│   ├── templates/jobs/          jobs.html, job_detail.html, job_form.html,
│   │                             student_dashboard.html, company_dashboard.html
│   └── urls.py
└── static/css/style.css     Single stylesheet shared by all apps
```



