import os
import re
import json
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

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
            # verify user exists in DB
            role = user.get("role")
            uid = user.get("id")
            if role == "student":
                if not Student.objects.filter(id=uid).exists():
                    return JsonResponse({"message": "User not found"}, status=401)
            elif role == "company":
                if not Company.objects.filter(id=uid).exists():
                    return JsonResponse({"message": "User not found"}, status=401)
            request.user_token = user
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def status(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    return JsonResponse({"status": "ok", "message": "UniHire API (Django) is running"})


@auth_required(roles=["student"])
def student_profile(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    uid = request.user_token.get("id")
    try:
        s = Student.objects.get(id=uid)
    except Student.DoesNotExist:
        return JsonResponse({"message": "Student profile not found"}, status=404)
    student = {"id": s.id, "name": s.name, "email": s.email, "university": s.university, "career": s.career, "semester": s.semester, "skills": s.skills, "certifications": s.certifications, "resume_filename": s.resume_filename}
    return JsonResponse({"student": student})


@csrf_exempt
@auth_required(roles=["student"])
def update_student_profile(request):
    if request.method not in ("PUT", "POST"):
        return HttpResponseNotAllowed(["PUT", "POST"])
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        data = {}
    required = [data.get(key) for key in ("name", "university", "career", "semester")]
    if not all(required):
        return JsonResponse({"message": "Missing required profile fields"}, status=400)
    # validate semester
    sem = str(data.get("semester"))
    if not sem.isdigit() or not (1 <= int(sem) <= 20):
        return JsonResponse({"message": "Semester must be a number between 1 and 20"}, status=400)
    uid = request.user_token.get("id")
    Student.objects.filter(id=uid).update(name=data.get("name"), university=data.get("university"), career=data.get("career"), semester=str(data.get("semester")), skills=data.get("skills", ""), certifications=data.get("certifications", ""), resume_filename=data.get("resume_filename", ""))
    s = Student.objects.get(id=uid)
    student = {"id": s.id, "name": s.name, "email": s.email, "university": s.university, "career": s.career, "semester": s.semester, "skills": s.skills, "certifications": s.certifications, "resume_filename": s.resume_filename}
    return JsonResponse({"message": "Profile updated successfully", "student": student}, status=201 if request.method == "POST" else 200)


@auth_required(roles=["company"])
def company_profile(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    uid = request.user_token.get("id")
    try:
        c = Company.objects.get(id=uid)
    except Company.DoesNotExist:
        return JsonResponse({"message": "Company profile not found"}, status=404)
    company = {"id": c.id, "company_name": c.company_name, "email": c.email}
    return JsonResponse({"company": company})


@csrf_exempt
@auth_required(roles=["company"])
def update_company_profile(request):
    if request.method not in ("PUT", "POST"):
        return HttpResponseNotAllowed(["PUT", "POST"])
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        data = {}
    name = data.get("companyName") or data.get("name")
    if not name:
        return JsonResponse({"message": "Company name is required"}, status=400)
    uid = request.user_token.get("id")
    Company.objects.filter(id=uid).update(company_name=name)
    c = Company.objects.get(id=uid)
    company = {"id": c.id, "company_name": c.company_name, "email": c.email}
    return JsonResponse({"message": "Company profile updated successfully", "company": company}, status=201 if request.method == "POST" else 200)


@csrf_exempt
def students_profile_dispatch(request):
    if request.method == "GET":
        return student_profile(request)
    if request.method in ("PUT", "POST"):
        return update_student_profile(request)
    return HttpResponseNotAllowed(["GET", "PUT", "POST"])


@csrf_exempt
def companies_profile_dispatch(request):
    if request.method == "GET":
        return company_profile(request)
    if request.method in ("PUT", "POST"):
        return update_company_profile(request)
    return HttpResponseNotAllowed(["GET", "PUT", "POST"])


@csrf_exempt
def applications_dispatch(request):
    if request.method == "GET":
        return student_applications(request)
    if request.method == "POST":
        return apply_to_job(request)
    return HttpResponseNotAllowed(["GET", "POST"])


def search_jobs(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    q = (request.GET.get("q") or "").strip().lower()
    job_type = (request.GET.get("job_type") or "").strip()
    location = (request.GET.get("location") or "").strip().lower()
    rows = Job.objects.all().order_by("-id")
    results = []
    for job in rows:
        matches_q = (not q) or (q in (job.title or "").lower()) or (q in (job.description or "").lower()) or (q in (job.required_skills or "").lower())
        matches_type = (not job_type) or job.job_type == job_type
        matches_loc = (not location) or (location in (job.location or "").lower())
        if matches_q and matches_type and matches_loc:
            results.append({"id": job.id, "company_id": job.company_id, "title": job.title, "description": job.description, "required_skills": job.required_skills, "location": job.location, "job_type": job.job_type, "created_at": job.created_at})
    return JsonResponse({"jobs": results, "count": len(results)})


@auth_required(roles=["student"])
def recommended_jobs(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    uid = request.user_token.get("id")
    try:
        s = Student.objects.get(id=uid)
    except Student.DoesNotExist:
        return JsonResponse({"jobs": []})
    skills = {item.strip().lower() for item in (s.skills or "").split(",") if item.strip()}
    applied = {a.job_id for a in Application.objects.filter(student_id=uid).values("job_id")}
    result = []
    for job in Job.objects.all().order_by("-id"):
        if job.id in applied:
            continue
        required = {item.strip().lower() for item in (job.required_skills or "").split(",") if item.strip()}
        matched = skills & required
        if matched:
            jd = {"id": job.id, "company_id": job.company_id, "title": job.title, "description": job.description, "required_skills": job.required_skills, "location": job.location, "job_type": job.job_type, "created_at": job.created_at}
            jd["matchCount"] = len(matched)
            jd["matchPercentage"] = round(len(matched) / len(required) * 100) if required else 0
            result.append(jd)
    result.sort(key=lambda job: job.get("matchCount", 0), reverse=True)
    return JsonResponse({"jobs": result})


@auth_required(roles=["company"])
def company_jobs(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    uid = request.user_token.get("id")
    rows = Job.objects.filter(company_id=uid).order_by("-id")
    jobs = [{"id": j.id, "company_id": j.company_id, "title": j.title, "description": j.description, "required_skills": j.required_skills, "location": j.location, "job_type": j.job_type, "created_at": j.created_at} for j in rows]
    return JsonResponse({"jobs": jobs})


@auth_required(roles=["student"])
def student_applications(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    uid = request.user_token.get("id")
    rows = Application.objects.filter(student_id=uid).select_related("job").order_by("-id")
    applications = []
    for a in rows:
        applications.append({"id": a.id, "status": a.status, "applied_at": a.applied_at, "job_id": a.job.id, "title": a.job.title, "description": a.job.description})
    return JsonResponse({"applications": applications})


@auth_required(roles=["company"])
def company_applicants(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    uid = request.user_token.get("id")
    rows = Application.objects.select_related("job", "student").filter(job__company_id=uid).order_by("-id")
    applicants = []
    for a in rows:
        applicants.append({"id": a.id, "status": a.status, "applied_at": a.applied_at, "job_id": a.job.id, "title": a.job.title, "student_id": a.student.id, "student_name": a.student.name})
    return JsonResponse({"applicants": applicants})


@csrf_exempt
@auth_required(roles=["company"])
def update_application_status(request, application_id):
    if request.method != "PUT":
        return HttpResponseNotAllowed(["PUT"])
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        data = {}
    status_val = data.get("status")
    if status_val not in {"Pending", "Accepted", "Rejected"}:
        return JsonResponse({"message": "Invalid application status"}, status=400)
    uid = request.user_token.get("id")
    try:
        app_obj = Application.objects.select_related("job").get(id=application_id, job__company_id=uid)
    except Application.DoesNotExist:
        return JsonResponse({"message": "Application not found"}, status=404)
    app_obj.status = status_val
    app_obj.save()
    return JsonResponse({"message": "Application status updated", "status": status_val})


@csrf_exempt
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


@csrf_exempt
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


@csrf_exempt
def jobs_list(request):
    # Support GET for listing and POST for creating (company)
    if request.method == "GET":
        jobs = []
        for job in Job.objects.all().order_by("-id"):
            d = {"id": job.id, "company_id": job.company_id, "title": job.title, "description": job.description, "required_skills": job.required_skills, "location": job.location, "job_type": job.job_type, "created_at": job.created_at}
            try:
                d["company_name"] = job.company.company_name
            except Exception:
                d["company_name"] = ""
            jobs.append(d)
        return JsonResponse({"jobs": jobs})
    elif request.method == "POST":
        # delegate to create_job logic (requires company)
        return create_job(request)
    else:
        return HttpResponseNotAllowed(["GET", "POST"])


def job_detail(request, job_id):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    try:
        job = Job.objects.select_related("company").get(id=job_id)
    except Job.DoesNotExist:
        return JsonResponse({"message": "Job not found"}, status=404)
    data = {"id": job.id, "title": job.title, "description": job.description, "required_skills": job.required_skills, "location": job.location, "job_type": job.job_type, "created_at": job.created_at}
    data["company_name"] = job.company.company_name
    data["company_id"] = job.company_id
    return JsonResponse({"job": data})


@csrf_exempt
def create_job(request):
    # expect POST (caller may call via jobs_list dispatcher)
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        data = {}
    # auth check
    header = request.META.get("HTTP_AUTHORIZATION", "")
    if not header.startswith("Bearer "):
        return JsonResponse({"message": "Token missing"}, status=401)
    user = decode_token(header.split(" ", 1)[1])
    if not user or user.get("role") != "company":
        return JsonResponse({"message": "Access denied"}, status=403)
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
    job_dict = {"id": job.id, "company_id": job.company_id, "title": job.title, "description": job.description, "required_skills": job.required_skills, "location": job.location, "job_type": job.job_type, "created_at": job.created_at}
    return JsonResponse({"message": "Job created successfully", "job": job_dict}, status=201)


@csrf_exempt
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
    # auth
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


