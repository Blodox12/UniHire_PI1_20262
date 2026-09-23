from django.contrib import messages
from django.contrib.auth import authenticate
from django.shortcuts import redirect, render

from .decorators import login_required
from .forms import (
    CompanyRegisterForm,
    CompanyProfileForm,
    LoginForm,
    StudentProfileForm,
    StudentRegisterForm,
)
from .models import Company, CustomUser, Student, StudentDocument
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
        form = StudentRegisterForm(request.POST, request.FILES)
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
                profile = Student.objects.create(
                    user=user,
                    name=data["name"].strip(),
                    email=email,
                    university=data["university"].strip(),
                    career=data["career"].strip(),
                    semester=data["semester"],
                    skills=data.get("skills", ""),
                    certifications=data.get("certifications", ""),
                    profile_photo=data.get("profile_photo"),
                    resume_filename=data.get("resume_filename"),
                )
                StudentDocument.objects.bulk_create(
                    [StudentDocument(student=profile, file=document) for document in data.get("documents", [])]
                )
                request.session["user_id"] = user.id
                request.session["role"] = "student"
                request.session["name"] = profile.name
                messages.success(request, "Account created successfully.")
                return redirect("jobs:student_dashboard")
        else:
            messages.error(request, "Please review the highlighted fields.")
    else:
        form = StudentRegisterForm()
    return render(request, "accounts/register_student.html", {"form": form})


def register_company(request):
    if request.method == "POST":
        form = CompanyRegisterForm(request.POST, request.FILES)
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
                profile = Company.objects.create(
                    user=user,
                    company_name=data["company_name"].strip(),
                    email=email,
                    profile_photo=data.get("profile_photo"),
                )
                request.session["user_id"] = user.id
                request.session["role"] = "company"
                request.session["name"] = profile.company_name
                messages.success(request, "Account created successfully.")
                return redirect("jobs:company_dashboard")
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
        form = StudentProfileForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            student.name = data["name"]
            student.university = data["university"]
            student.career = data["career"]
            student.semester = data["semester"]
            student.skills = data.get("skills", "")
            student.certifications = data.get("certifications", "")
            if data.get("profile_photo"):
                student.profile_photo = data["profile_photo"]
            if data.get("resume_filename"):
                student.resume_filename = data["resume_filename"]
            student.save()
            StudentDocument.objects.bulk_create(
                [StudentDocument(student=student, file=document) for document in data.get("documents", [])]
            )
            messages.success(request, "Profile updated successfully.")
    else:
        form = StudentProfileForm(initial={
            "name": student.name,
            "university": student.university,
            "career": student.career,
            "semester": student.semester,
            "skills": student.skills,
            "certifications": student.certifications,
        })
    return render(request, "accounts/profile.html", {"form": form, "student": student})


@login_required(role="company")
def company_profile_view(request):
    company = Company.objects.filter(user_id=request.session.get("user_id")).first()
    if request.method == "POST":
        form = CompanyProfileForm(request.POST, request.FILES)
        if form.is_valid():
            company.company_name = form.cleaned_data["company_name"]
            if form.cleaned_data.get("profile_photo"):
                company.profile_photo = form.cleaned_data["profile_photo"]
            company.save()
            request.session["name"] = company.company_name
            messages.success(request, "Profile updated successfully.")
            return redirect("jobs:company_dashboard")
    else:
        form = CompanyProfileForm(initial={
            "company_name": company.company_name,
        })
    return render(request, "accounts/company_profile.html", {"form": form, "company": company})
