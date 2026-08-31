# UniHire

*Helping university students find their first professional opportunities through skill-based job matching.*

---

#  Table of Contents

1. [Overview](#overview)
2. [Problem Statement](#problem-statement)

---

#  Overview

**UniHire** is a web platform designed to help university students obtain their first professional experience.

Instead of focusing on previous work experience, UniHire matches students with internships and entry-level job opportunities according to their academic knowledge, technical skills, certifications, and interests.

---

#  Problem Statement

Many university students struggle to find employment because:

- They have little or no professional experience.
- They lack recommendations.
- They do not know which vacancies fit their current skills.
- Companies often prioritize experienced candidates.

## Technology

- Backend: Python 3.10+ with Flask, SQLite, and JWT.
- Frontend: React with Vite.
- Database: SQLite at `backend/database/unihire.db`.

## Local Execution

### 1. Python backend

From the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

The API is available at `http://localhost:5000`. On Linux or macOS, activate the environment with `source .venv/bin/activate`.

### 2. React frontend

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The frontend uses `VITE_API_URL` when defined; otherwise it connects to `http://localhost:5000`.

## End-to-end evidence

The automated tests use a temporary SQLite database and cover student and company registration, login, JWT authentication, duplicate emails, input validation, API status, job listing, and protected profile access.

```powershell
cd backend
python -m unittest test_api.py -v
```

Verified result:

```text
test_company_can_create_update_and_delete_own_job ... ok
test_company_registration_and_duplicate_email ... ok
test_job_detail_endpoint ... ok
test_registration_rejects_weak_password_and_invalid_email ... ok
test_student_registration_login_and_application_flow ... ok
Ran 5 tests
OK
```

Manual health check while the backend is running:

```powershell
Invoke-RestMethod http://localhost:5000/api/status
```

Expected response:

```json
{"message":"UniHire API is running","status":"ok"}
```

---
# Requirements
1. Functional Requirements (FR)

FR-01. User Registration and Authentication
The system shall allow students and companies to register and log in using an email address and password.

FR-02. Student Profile Management
The system shall allow students to create and update a profile containing their academic information, technical skills, certifications, interests, and resume.

FR-03. Job Posting Management
The system shall allow companies to create, edit, and manage internship and entry-level job postings, including job descriptions, required skills, and qualifications.

FR-04. Job Recommendation and Application
The system shall recommend job opportunities to students based on the compatibility between their profiles and the job requirements, allowing them to apply directly through the platform.

FR-05. Job Search and Filtering

The system shall allow students to search and filter job opportunities by location, job category, required skills, and work modality.

FR-06. Resume Upload

The system shall allow students to upload and update their resume in PDF format.

FR-07. Application Tracking

The system shall allow students to view the status of their job applications (e.g., Submitted, Under Review, Accepted, or Rejected).

FR-08. Applicant Management

The system shall allow companies to review the profiles and resumes of students who have applied for their job postings.

FR-09. Notifications

The system shall notify students when new job opportunities match their profiles or when the status of an application changes.

FR-10. Profile Editing

The system shall allow both students and companies to edit and update their personal or organizational information at any time.

FR-11. Password Recovery

The system shall provide users with a password recovery feature through email verification.

FR-12. Job Post Deletion

The system shall allow companies to edit or delete their published job opportunities.

2. Non-Functional Requirements (NFR)

NFR-01. Performance
The system shall display job search results and recommendations within a maximum response time of 3 seconds under normal operating conditions.

NFR-02. Security
The system shall protect users' personal information by implementing secure authentication and encrypted password storage.

NFR-03. Availability
The platform shall maintain an availability of at least 99%, excluding scheduled maintenance periods.

NFR-04. Usability
The system shall provide an intuitive and responsive user interface, ensuring compatibility with desktop computers, tablets, and mobile devices.

NFR-05. Scalability

The system shall support at least 1,000 concurrent users without significant degradation in performance.

NFR-06. Browser Compatibility

The system shall be fully compatible with the latest versions of Google Chrome, Mozilla Firefox, Microsoft Edge, and Safari.

NFR-07. Data Integrity

The system shall ensure the consistency and integrity of user and job data during all database transactions.

NFR-08. Maintainability

The system shall be developed using a modular architecture to facilitate maintenance, debugging, and future enhancements.

NFR-09. Backup

The system shall perform automatic database backups at least once every 24 hours.

NFR-10. Accessibility

The system shall comply with the WCAG 2.1 Level AA accessibility guidelines to ensure usability for people with disabilities.

NFR-11. Reliability

The system shall recover from unexpected failures without losing previously stored user information.

NFR-12. Privacy

The system shall ensure that users' personal information is only accessible to authorized users in accordance with applicable data protection regulations.
