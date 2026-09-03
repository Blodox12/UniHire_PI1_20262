from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect, render

from .decorators import login_required
from .forms import (
    CompanyRegisterForm,
    LoginForm,
    StudentProfileForm,
    StudentRegisterForm,
)
from .models import Company, Student
from .utils import current_student

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


def login_view(request):
    role = request.GET.get("role", "student")
    if request.method == "POST":
        form = LoginForm(request.POST)
        role = request.POST.get("role", "student")
        if form.is_valid():
            data = form.cleaned_data
            email = data["email"].strip().lower()
            password = data["password"]
            model = Student if data["role"] == "student" else Company
            user = model.objects.filter(email=email).first()
            if not user:
                messages.error(request, "User not found")
            elif not check_password(password, user.password):
                messages.error(request, "Invalid password")
            else:
                request.session["user_id"] = user.id
                request.session["role"] = data["role"]
                request.session["name"] = getattr(user, "name", getattr(user, "company_name", ""))
                return redirect(
                    "jobs:company_dashboard" if data["role"] == "company" else "jobs:student_dashboard"
                )
        else:
            messages.error(request, "Missing required fields")
    return render(request, "accounts/login.html", {"role": role})


def logout_view(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect("core:home")


def register_student(request):
    if request.method == "POST":
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if Student.objects.filter(email=data["email"]).exists() or Company.objects.filter(email=data["email"]).exists():
                messages.error(request, "User already exists")
            else:
                Student.objects.create(
                    name=data["name"].strip(),
                    email=data["email"],
                    password=make_password(data["password"]),
                    university=data["university"].strip(),
                    career=data["career"].strip(),
                    semester=data["semester"],
                    skills=data.get("skills", ""),
                    certifications=data.get("certifications", ""),
                    resume_filename=data.get("resume_filename", ""),
                )
                messages.success(request, "Account created successfully. Please log in.")
                return redirect("accounts:login")
        else:
            messages.error(request, "Please review the highlighted fields.")
    else:
        form = StudentRegisterForm()
    return render(request, "accounts/register_student.html", {"form": form})


def register_company(request):
    if request.method == "POST":
        form = CompanyRegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if Company.objects.filter(email=data["email"]).exists() or Student.objects.filter(email=data["email"]).exists():
                messages.error(request, "User already exists")
            else:
                Company.objects.create(
                    company_name=data["company_name"].strip(),
                    email=data["email"],
                    password=make_password(data["password"]),
                )
                messages.success(request, "Account created successfully. Please log in.")
                return redirect("accounts:login")
        else:
            messages.error(request, "Please review the highlighted fields.")
    else:
        form = CompanyRegisterForm()
    return render(request, "accounts/register_company.html", {"form": form})


# ---------------------------------------------------------------------------
# Student profile
# ---------------------------------------------------------------------------


@login_required(role="student")
def profile_view(request):
    student = current_student(request)
    if request.method == "POST":
        form = StudentProfileForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            student.name = data["name"]
            student.university = data["university"]
            student.career = data["career"]
            student.semester = data["semester"]
            student.skills = data.get("skills", "")
            student.certifications = data.get("certifications", "")
            student.resume_filename = data.get("resume_filename", "")
            student.save()
            messages.success(request, "Profile updated successfully.")
    else:
        form = StudentProfileForm(initial={
            "name": student.name,
            "university": student.university,
            "career": student.career,
            "semester": student.semester,
            "skills": student.skills,
            "certifications": student.certifications,
            "resume_filename": student.resume_filename,
        })
    return render(request, "accounts/profile.html", {"form": form})
