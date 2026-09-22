from django.contrib import messages
from django.contrib.auth import authenticate
from django.shortcuts import redirect, render

from .decorators import login_required
from .forms import (
    CompanyRegisterForm,
    LoginForm,
    StudentProfileForm,
    StudentRegisterForm,
)
from .models import Company, CustomUser, Student
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
            user = authenticate(request, email=email, password=password)
            if not user or user.role != data["role"]:
                messages.error(request, "User not found or invalid password")
            else:
                request.session["user_id"] = user.id
                request.session["role"] = data["role"]
                profile = Student.objects.filter(user=user).first() or Company.objects.filter(user=user).first()
                request.session["name"] = getattr(profile, "name", getattr(profile, "company_name", ""))
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
            email = data["email"].strip().lower()
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "User already exists")
            else:
                user = CustomUser.objects.create_user(
                    email=email,
                    password=data["password"],
                    role="student",
                )
                Student.objects.create(
                    user=user,
                    name=data["name"].strip(),
                    email=email,
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
            email = data["email"].strip().lower()
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "User already exists")
            else:
                user = CustomUser.objects.create_user(
                    email=email,
                    password=data["password"],
                    role="company",
                )
                Company.objects.create(
                    user=user,
                    company_name=data["company_name"].strip(),
                    email=email,
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
