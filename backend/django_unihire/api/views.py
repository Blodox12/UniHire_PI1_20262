import os
import re
import json
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

from django.http import JsonResponse, HttpResponseNotAllowed

from .models import Student, Company, Job, Application


JWT_SECRET = os.getenv("JWT_SECRET", "unihire-secret")


def token_for(user_id, role):
    return jwt.encode({"id": user_id, "role": role, "exp": datetime.now(timezone.utc) + timedelta(days=7)}, JWT_SECRET, algorithm="HS256")


def decode_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except Exception:
        return None


def auth_required(roles=None):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            header = request.META.get("HTTP_AUTHORIZATION", "")
            if not header.startswith("Bearer "):
                return JsonResponse({"message": "Token missing"}, status=401)
            user = decode_token(header.split(" ", 1)[1])
            if not user:
                return JsonResponse({"message": "Invalid token"}, status=401)
            if roles and user.get("role") not in roles:
                return JsonResponse({"message": "Access denied"}, status=403)
            request.user_token = user
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def status(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    return JsonResponse({"status": "ok", "message": "UniHire API (Django) is running"})


def register(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        data = {}
    role = data.get("role")
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not role or not email or not password:
        return JsonResponse({"message": "Missing required fields"}, status=400)
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        return JsonResponse({"message": "Invalid email"}, status=400)
    if len(password) < 6:
        return JsonResponse({"message": "Password must contain at least 6 characters"}, status=400)
    if Student.objects.filter(email=email).exists() or Company.objects.filter(email=email).exists():
        return JsonResponse({"message": "User already exists"}, status=400)
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    if role == "student":
        name = data.get("name") or ""
        university = data.get("university") or ""
        career = data.get("career") or ""
        semester = str(data.get("semester") or "")
        if not all([name.strip(), university.strip(), career.strip(), semester.strip()]):
            return JsonResponse({"message": "Student profile data is incomplete"}, status=400)
        Student.objects.create(name=name.strip(), email=email, password=hashed, university=university.strip(), career=career.strip(), semester=semester.strip(), skills=data.get("skills", ""), certifications=data.get("certifications", ""), resume_filename=data.get("resume_filename", ""))
    elif role == "company":
        company_name = data.get("companyName") or data.get("name")
        if not company_name:
            return JsonResponse({"message": "Company name is required"}, status=400)
        Company.objects.create(company_name=company_name, email=email, password=hashed)
    else:
        return JsonResponse({"message": "Invalid role"}, status=400)
    return JsonResponse({"message": "Account created successfully"}, status=201)


def login(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        data = {}
    role = data.get("role")
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not role or not email or not password:
        return JsonResponse({"message": "Missing required fields"}, status=400)
    if role == "student":
        try:
            user = Student.objects.get(email=email)
        except Student.DoesNotExist:
            return JsonResponse({"message": "User not found"}, status=404)
    elif role == "company":
        try:
            user = Company.objects.get(email=email)
        except Company.DoesNotExist:
            return JsonResponse({"message": "User not found"}, status=404)
    else:
        return JsonResponse({"message": "Invalid role"}, status=400)
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        return JsonResponse({"message": "Invalid password"}, status=401)
    public_user = {"id": user.id, "role": role, "name": getattr(user, "name", getattr(user, "company_name", "")), "email": user.email}
    return JsonResponse({"token": token_for(user.id, role), "user": public_user})


def jobs_list(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    jobs = list(Job.objects.all().order_by("-id").values())
    return JsonResponse({"jobs": jobs})


def job_detail(request, job_id):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    try:
        job = Job.objects.select_related("company").get(id=job_id)
    except Job.DoesNotExist:
        return JsonResponse({"message": "Job not found"}, status=404)
    data = {k: v for k, v in job.__dict__.items() if not k.startswith("_") and k != "company_id"}
    data["company_name"] = job.company.company_name
    return JsonResponse({"job": data})


def create_job(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    # auth
    header = request.META.get("HTTP_AUTHORIZATION", "")
    if not header.startswith("Bearer "):
        return JsonResponse({"message": "Token missing"}, status=401)
    user = decode_token(header.split(" ", 1)[1])
    if not user or user.get("role") != "company":
        return JsonResponse({"message": "Access denied"}, status=403)
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        data = {}
    required = [str(data.get(k, "")).strip() for k in ("title", "description", "required_skills", "location")]
    if not all(required):
        return JsonResponse({"message": "Missing job fields"}, status=400)
    job_type = data.get("job_type", "Remote")
    if job_type not in {"Remote", "Hybrid", "On-site"}:
        return JsonResponse({"message": "Invalid job type"}, status=400)
    company_id = user.get("id")
    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        return JsonResponse({"message": "User not found"}, status=401)
    job = Job.objects.create(company=company, title=required[0], description=required[1], required_skills=required[2], location=required[3], job_type=job_type)
    return JsonResponse({"message": "Job created successfully", "job": {k: v for k, v in job.__dict__.items() if not k.startswith("_") and k != "company_id"}}, status=201)


def apply_to_job(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        data = {}
    job_id = data.get("jobId")
    if isinstance(job_id, bool) or not isinstance(job_id, int) or job_id < 1:
        return JsonResponse({"message": "Job id is required"}, status=400)
    header = request.META.get("HTTP_AUTHORIZATION", "")
    if not header.startswith("Bearer "):
        return JsonResponse({"message": "Token missing"}, status=401)
    user = decode_token(header.split(" ", 1)[1])
    if not user or user.get("role") != "student":
        return JsonResponse({"message": "Access denied"}, status=403)
    student_id = user.get("id")
    if Application.objects.filter(student_id=student_id, job_id=job_id).exists():
        return JsonResponse({"message": "You already applied to this job"}, status=400)
    if not Job.objects.filter(id=job_id).exists():
        return JsonResponse({"message": "Job not found"}, status=404)
    Application.objects.create(student_id=student_id, job_id=job_id, status="Pending")
    return JsonResponse({"message": "Application submitted successfully"}, status=201)


