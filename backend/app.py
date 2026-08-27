import os
import sqlite3
from datetime import datetime, timedelta, timezone
from functools import wraps
from pathlib import Path

import bcrypt
import jwt
from flask import Flask, g, jsonify, request
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database" / "unihire.db"
JWT_SECRET = os.getenv("JWT_SECRET", "unihire-secret")

app = Flask(__name__)
CORS(app)


def get_db():
    if "db" not in g:
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_one(sql, params=()):
    return get_db().execute(sql, params).fetchone()


def query_all(sql, params=()):
    return get_db().execute(sql, params).fetchall()


def execute(sql, params=()):
    db = get_db()
    cursor = db.execute(sql, params)
    db.commit()
    return cursor


def initialize_database():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
            university TEXT, career TEXT, semester TEXT, skills TEXT,
            certifications TEXT, resume_filename TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT, company_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, company_id INTEGER NOT NULL,
            title TEXT NOT NULL, description TEXT NOT NULL,
            required_skills TEXT NOT NULL, location TEXT NOT NULL,
            job_type TEXT NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id)
        );
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL, status TEXT DEFAULT 'Pending',
            applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(id),
            FOREIGN KEY(job_id) REFERENCES jobs(id)
        );
        """
    )
    db.commit()


def row_dict(row):
    return dict(row) if row else None


def token_for(user_id, role):
    return jwt.encode(
        {"id": user_id, "role": role, "exp": datetime.now(timezone.utc) + timedelta(days=7)},
        JWT_SECRET,
        algorithm="HS256",
    )


def protect(*roles):
    def decorator(handler):
        @wraps(handler)
        def wrapped(*args, **kwargs):
            header = request.headers.get("Authorization", "")
            if not header.startswith("Bearer "):
                return jsonify(message="Token missing"), 401
            try:
                user = jwt.decode(header.split(" ", 1)[1], JWT_SECRET, algorithms=["HS256"])
            except (jwt.InvalidTokenError, IndexError):
                return jsonify(message="Invalid token"), 401
            if roles and user.get("role") not in roles:
                return jsonify(message="Access denied"), 403
            table = "companies" if user.get("role") == "company" else "students"
            if not query_one(f"SELECT id FROM {table} WHERE id = ?", (user.get("id"),)):
                return jsonify(message="User not found"), 401
            g.user = user
            return handler(*args, **kwargs)
        return wrapped
    return decorator


@app.get("/api/status")
def status():
    return jsonify(status="ok", message="UniHire API is running")


@app.post("/api/auth/register")
def register():
    data = request.get_json(silent=True) or {}
    role = data.get("role")
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not role or not email or not password:
        return jsonify(message="Missing required fields"), 400
    if "@" not in email:
        return jsonify(message="Invalid email"), 400
    if len(password) < 6:
        return jsonify(message="Password must contain at least 6 characters"), 400
    if query_one("SELECT id FROM students WHERE email = ?", (email,)) or query_one("SELECT id FROM companies WHERE email = ?", (email,)):
        return jsonify(message="User already exists"), 400
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    if role == "student":
        fields = [data.get(key, "") for key in ("name", "university", "career", "semester")]
        if not all(fields):
            return jsonify(message="Student profile data is incomplete"), 400
        execute("INSERT INTO students (name,email,password,university,career,semester,skills,certifications,resume_filename) VALUES (?,?,?,?,?,?,?,?,?)", (fields[0], email, hashed, *fields[1:], data.get("skills", ""), data.get("certifications", ""), data.get("resume_filename", "")))
    elif role == "company":
        company_name = data.get("companyName") or data.get("name")
        if not company_name:
            return jsonify(message="Company name is required"), 400
        execute("INSERT INTO companies (company_name,email,password) VALUES (?,?,?)", (company_name, email, hashed))
    else:
        return jsonify(message="Invalid role"), 400
    return jsonify(message="Account created successfully"), 201


@app.post("/api/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    role = data.get("role")
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not role or not email or not password:
        return jsonify(message="Missing required fields"), 400
    if role == "student":
        user = query_one("SELECT id,name,email,password FROM students WHERE email = ?", (email,))
    elif role == "company":
        user = query_one("SELECT id,company_name AS name,email,password FROM companies WHERE email = ?", (email,))
    else:
        return jsonify(message="Invalid role"), 400
    if not user:
        return jsonify(message="User not found"), 404
    if not bcrypt.checkpw(password.encode(), user["password"].encode()):
        return jsonify(message="Invalid password"), 401
    public_user = {"id": user["id"], "role": role, "name": user["name"], "email": user["email"]}
    return jsonify(token=token_for(user["id"], role), user=public_user)


@app.get("/api/students/profile")
@protect("student")
def student_profile():
    student = query_one("SELECT * FROM students WHERE id = ?", (g.user["id"],))
    return jsonify(student=row_dict(student)) if student else (jsonify(message="Student profile not found"), 404)


@app.put("/api/students/profile")
@app.post("/api/students/profile")
@protect("student")
def update_student_profile():
    data = request.get_json(silent=True) or {}
    required = [data.get(key) for key in ("name", "university", "career", "semester")]
    if not all(required):
        return jsonify(message="Missing required profile fields"), 400
    execute("UPDATE students SET name=?,university=?,career=?,semester=?,skills=?,certifications=?,resume_filename=? WHERE id=?", (*required, data.get("skills", ""), data.get("certifications", ""), data.get("resume_filename", ""), g.user["id"]))
    return jsonify(message="Profile updated successfully", student=row_dict(query_one("SELECT * FROM students WHERE id = ?", (g.user["id"],)))), 201 if request.method == "POST" else 200


@app.get("/api/companies/profile")
@protect("company")
def company_profile():
    company = query_one("SELECT * FROM companies WHERE id = ?", (g.user["id"],))
    return jsonify(company=row_dict(company)) if company else (jsonify(message="Company profile not found"), 404)


@app.put("/api/companies/profile")
@app.post("/api/companies/profile")
@protect("company")
def update_company_profile():
    name = (request.get_json(silent=True) or {}).get("companyName")
    if not name:
        return jsonify(message="Company name is required"), 400
    execute("UPDATE companies SET company_name=? WHERE id=?", (name, g.user["id"]))
    return jsonify(message="Company profile updated successfully", company=row_dict(query_one("SELECT * FROM companies WHERE id = ?", (g.user["id"],)))), 201 if request.method == "POST" else 200


@app.get("/api/jobs")
def jobs():
    return jsonify(jobs=[row_dict(row) for row in query_all("SELECT * FROM jobs ORDER BY id DESC")])


@app.get("/api/jobs/recommended")
@protect("student")
def recommended_jobs():
    student = query_one("SELECT skills FROM students WHERE id=?", (g.user["id"],))
    skills = {item.strip().lower() for item in (student["skills"] or "").split(",") if item.strip()}
    result = []
    for row in query_all("SELECT * FROM jobs ORDER BY id DESC"):
        job = row_dict(row)
        required = {item.strip().lower() for item in (job["required_skills"] or "").split(",") if item.strip()}
        job["matchCount"] = len(skills & required)
        result.append(job)
    result.sort(key=lambda job: job["matchCount"], reverse=True)
    return jsonify(jobs=result)


@app.post("/api/jobs")
@protect("company")
def create_job():
    data = request.get_json(silent=True) or {}
    required = [data.get(key) for key in ("title", "description", "required_skills", "location")]
    if not all(required):
        return jsonify(message="Missing job fields"), 400
    execute("INSERT INTO jobs (company_id,title,description,required_skills,location,job_type) VALUES (?,?,?,?,?,?)", (g.user["id"], *required, data.get("job_type", "Remote")))
    return jsonify(message="Job created successfully"), 201


@app.put("/api/jobs/<int:job_id>")
@protect("company")
def update_job(job_id):
    if not query_one("SELECT id FROM jobs WHERE id=? AND company_id=?", (job_id, g.user["id"])):
        return jsonify(message="Job not found"), 404
    data = request.get_json(silent=True) or {}
    required = [data.get(key) for key in ("title", "description", "required_skills", "location")]
    if not all(required):
        return jsonify(message="Missing job fields"), 400
    execute("UPDATE jobs SET title=?,description=?,required_skills=?,location=?,job_type=? WHERE id=?", (*required, data.get("job_type", "Remote"), job_id))
    return jsonify(message="Job updated successfully")


@app.delete("/api/jobs/<int:job_id>")
@protect("company")
def delete_job(job_id):
    if not query_one("SELECT id FROM jobs WHERE id=? AND company_id=?", (job_id, g.user["id"])):
        return jsonify(message="Job not found"), 404
    execute("DELETE FROM applications WHERE job_id=?", (job_id,))
    execute("DELETE FROM jobs WHERE id=?", (job_id,))
    return jsonify(message="Job deleted successfully")


@app.get("/api/companies/jobs")
@protect("company")
def company_jobs():
    return jsonify(jobs=[row_dict(row) for row in query_all("SELECT * FROM jobs WHERE company_id=? ORDER BY id DESC", (g.user["id"],))])


@app.post("/api/applications")
@protect("student")
def apply_to_job():
    job_id = (request.get_json(silent=True) or {}).get("jobId")
    if not job_id:
        return jsonify(message="Job id is required"), 400
    if query_one("SELECT id FROM applications WHERE student_id=? AND job_id=?", (g.user["id"], job_id)):
        return jsonify(message="You already applied to this job"), 400
    if not query_one("SELECT id FROM jobs WHERE id=?", (job_id,)):
        return jsonify(message="Job not found"), 404
    execute("INSERT INTO applications (student_id,job_id,status) VALUES (?,?,?)", (g.user["id"], job_id, "Pending"))
    return jsonify(message="Application submitted successfully"), 201


@app.get("/api/applications")
@protect("student")
def student_applications():
    rows = query_all("SELECT a.id,a.status,a.applied_at,j.title,j.description FROM applications a JOIN jobs j ON j.id=a.job_id WHERE a.student_id=? ORDER BY a.id DESC", (g.user["id"],))
    return jsonify(applications=[row_dict(row) for row in rows])


@app.get("/api/applications/company")
@protect("company")
def company_applicants():
    rows = query_all("SELECT a.id,a.status,a.applied_at,j.title,s.name AS student_name FROM applications a JOIN jobs j ON j.id=a.job_id JOIN students s ON s.id=a.student_id WHERE j.company_id=? ORDER BY a.id DESC", (g.user["id"],))
    return jsonify(applicants=[row_dict(row) for row in rows])


if __name__ == "__main__":
    with app.app_context():
        initialize_database()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
