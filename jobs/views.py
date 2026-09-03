from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from accounts.decorators import login_required
from accounts.utils import current_company, current_student

from .forms import JobForm
from .models import Application, Job

# ---------------------------------------------------------------------------
# Jobs (public browsing + search/filter, ported from /api/jobs/search)
# ---------------------------------------------------------------------------


def jobs_view(request):
    q = (request.GET.get("q") or "").strip()
    job_type = (request.GET.get("job_type") or "").strip()
    location = (request.GET.get("location") or "").strip()

    jobs = Job.objects.select_related("company").all()
    if q:
        from django.db.models import Q
        jobs = jobs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(required_skills__icontains=q))
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if location:
        jobs = jobs.filter(location__icontains=location)

    applied_ids = set()
    student = current_student(request)
    if student:
        applied_ids = set(Application.objects.filter(student=student).values_list("job_id", flat=True))

    context = {
        "jobs": jobs,
        "applied_ids": applied_ids,
        "search": q,
        "job_type": job_type,
        "location": location,
        "has_filters": bool(q or job_type or location),
    }
    return render(request, "jobs/jobs.html", context)


def job_detail(request, job_id):
    job = get_object_or_404(Job.objects.select_related("company"), id=job_id)
    has_applied = False
    student = current_student(request)
    if student:
        has_applied = Application.objects.filter(student=student, job=job).exists()
    return render(request, "jobs/job_detail.html", {"job": job, "has_applied": has_applied})


@require_POST
def apply_to_job(request, job_id):
    student = current_student(request)
    if not student:
        messages.error(request, "Only students can apply to jobs. Please log in as a student.")
        return redirect("accounts:login")
    job = get_object_or_404(Job, id=job_id)
    if Application.objects.filter(student=student, job=job).exists():
        messages.error(request, "You already applied to this job")
    else:
        Application.objects.create(student=student, job=job, status="Pending")
        messages.success(request, "Application submitted successfully!")
    next_url = request.POST.get("next") or "jobs:jobs"
    if next_url == "jobs:job_detail":
        return redirect("jobs:job_detail", job_id=job.id)
    return redirect("jobs:jobs")


@login_required(role="company")
def create_job(request):
    company = current_company(request)
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = company
            job.save()
            messages.success(request, "Job posted successfully.")
            return redirect("jobs:company_dashboard")
    else:
        form = JobForm()
    return render(request, "jobs/job_form.html", {"form": form, "is_editing": False})


@login_required(role="company")
def edit_job(request, job_id):
    company = current_company(request)
    job = get_object_or_404(Job, id=job_id, company=company)
    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully.")
            return redirect("jobs:company_dashboard")
    else:
        form = JobForm(instance=job)
    return render(request, "jobs/job_form.html", {"form": form, "is_editing": True, "job": job})


@login_required(role="company")
@require_POST
def delete_job(request, job_id):
    company = current_company(request)
    job = get_object_or_404(Job, id=job_id, company=company)
    job.delete()
    messages.success(request, "Job deleted successfully.")
    return redirect("jobs:company_dashboard")


# ---------------------------------------------------------------------------
# Student dashboard
# ---------------------------------------------------------------------------


@login_required(role="student")
def student_dashboard(request):
    student = current_student(request)
    view = request.GET.get("view", "profile")

    recommended_jobs = []
    applications = []

    if view == "recommended":
        skills = {item.strip().lower() for item in (student.skills or "").split(",") if item.strip()}
        applied_ids = set(Application.objects.filter(student=student).values_list("job_id", flat=True))
        for job in Job.objects.exclude(id__in=applied_ids):
            required = {item.strip().lower() for item in (job.required_skills or "").split(",") if item.strip()}
            matched = skills & required
            if matched:
                job.match_count = len(matched)
                job.match_percentage = round(len(matched) / len(required) * 100) if required else 0
                recommended_jobs.append(job)
        recommended_jobs.sort(key=lambda j: j.match_count, reverse=True)
    elif view == "applications":
        applications = Application.objects.filter(student=student).select_related("job")

    context = {
        "student": student,
        "view": view,
        "recommended_jobs": recommended_jobs,
        "applications": applications,
    }
    return render(request, "jobs/student_dashboard.html", context)


# ---------------------------------------------------------------------------
# Company dashboard
# ---------------------------------------------------------------------------


@login_required(role="company")
def company_dashboard(request):
    company = current_company(request)
    view = request.GET.get("view", "jobs")

    jobs = []
    applicants = []
    if view == "applicants":
        applicants = Application.objects.select_related("job", "student").filter(job__company=company)
    else:
        jobs = Job.objects.filter(company=company)

    context = {
        "company": company,
        "view": view,
        "jobs": jobs,
        "applicants": applicants,
    }
    return render(request, "jobs/company_dashboard.html", context)


@login_required(role="company")
@require_POST
def update_application_status(request, application_id):
    company = current_company(request)
    application = get_object_or_404(
        Application.objects.select_related("job"), id=application_id, job__company=company
    )
    status_val = request.POST.get("status")
    if status_val not in {"Pending", "Accepted", "Rejected"}:
        messages.error(request, "Invalid application status")
    else:
        application.status = status_val
        application.save()
        messages.success(request, "Application status updated.")
    return redirect(f"{reverse('jobs:company_dashboard')}?view=applicants")
