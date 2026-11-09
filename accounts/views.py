from django.contrib import messages
from django.contrib.auth import authenticate
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .decorators import login_required
from .forms import (
    CompanyRegisterForm,
    CompanyProfileForm,
    DeleteAccountForm,
    LoginForm,
    StudentProfileForm,
    StudentRegisterForm,
)
from .models import Company, CustomUser, Student, StudentDocument
from .utils import current_student

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


def resolve_login_email(identifier):
    """The login field accepts an email or a username; returns the email to authenticate."""
    identifier = identifier.strip()
    if "@" in identifier:
        return identifier.lower()
    user = CustomUser.objects.filter(username__iexact=identifier).first()
    return user.email if user else identifier.lower()


def login_view(request):
    role = request.GET.get("role", "student")
    if request.method == "POST":
        form = LoginForm(request.POST)
        role = request.POST.get("role", "student")
        if form.is_valid():
            data = form.cleaned_data
            email = resolve_login_email(data["identifier"])
            password = data["password"]
            user = authenticate(request, email=email, password=password)
            if not user or user.role != data["role"]:
                messages.error(request, "User not found or invalid password")
            else:
                # New session key on login to prevent session fixation.
                request.session.cycle_key()
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
            if CustomUser.objects.filter(email=email).exists() or Student.objects.filter(email=email).exists():
                messages.error(request, "User already exists")
            else:
                # User, profile and documents are saved together or not at all (NFR-07).
                with transaction.atomic():
                    user = CustomUser.objects.create_user(
                        email=email,
                        username=data["username"],
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
            if CustomUser.objects.filter(email=email).exists() or Company.objects.filter(email=email).exists():
                messages.error(request, "User already exists")
            else:
                # User and company profile are saved together or not at all (NFR-07).
                with transaction.atomic():
                    user = CustomUser.objects.create_user(
                        email=email,
                        username=data["username"],
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
                messages.success(
                    request,
                    "Account created. An administrator will review your company before you can publish jobs.",
                )
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
        form = StudentProfileForm(request.POST, request.FILES, user_id=student.user_id)
        if form.is_valid():
            data = form.cleaned_data
            if data["username"] and student.user:
                student.user.username = data["username"]
                student.user.save(update_fields=["username"])
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
            "username": student.user.username if student.user else "",
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
        form = CompanyProfileForm(request.POST, request.FILES, user_id=company.user_id)
        if form.is_valid():
            if form.cleaned_data["username"] and company.user:
                company.user.username = form.cleaned_data["username"]
                company.user.save(update_fields=["username"])
            company.company_name = form.cleaned_data["company_name"]
            if form.cleaned_data.get("profile_photo"):
                company.profile_photo = form.cleaned_data["profile_photo"]
            company.save()
            request.session["name"] = company.company_name
            messages.success(request, "Profile updated successfully.")
            return redirect("jobs:company_dashboard")
    else:
        form = CompanyProfileForm(initial={
            "username": company.user.username if company.user else "",
            "company_name": company.company_name,
        })
    return render(request, "accounts/company_profile.html", {"form": form, "company": company})


# ---------------------------------------------------------------------------
# Account deletion (NFR-12): users can erase their account and personal files.
# ---------------------------------------------------------------------------


def _uploaded_files(user):
    """Files on disk that belong to the user and must be removed with the account."""
    files = []
    student = Student.objects.filter(user=user).first()
    if student:
        files += [student.profile_photo, student.resume_filename]
        files += [document.file for document in student.documents.all()]
        files += [application.resume for application in student.applications.all()]
    company = Company.objects.filter(user=user).first()
    if company:
        from jobs.models import Application

        files.append(company.profile_photo)
        files += [application.resume for application in Application.objects.filter(job__company=company)]
    return [file for file in files if file]


@login_required()
@require_POST
def delete_account(request):
    user = CustomUser.objects.filter(id=request.session.get("user_id")).first()
    back = "accounts:company_profile" if request.session.get("role") == "company" else "accounts:profile"
    form = DeleteAccountForm(request.POST)
    if not user or not form.is_valid() or not user.check_password(form.cleaned_data["password"]):
        messages.error(request, "Incorrect password. Your account was not deleted.")
        return redirect(back)

    files = _uploaded_files(user)
    # Deleting the user cascades to the profile, documents, jobs and applications.
    with transaction.atomic():
        user.delete()
    for file in files:
        file.delete(save=False)

    request.session.flush()
    messages.success(request, "Your account and personal data were deleted.")
    return redirect("core:home")
