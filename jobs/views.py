from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from accounts.decorators import login_required
from accounts.utils import current_company, current_student

from .forms import JobForm, ResumeForm
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

    history_filter = request.GET.get("status", "")
    history_counts = {}

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
    elif view == "history":
        all_apps = Application.objects.filter(student=student).select_related("job", "job__company")
        history_counts = {
            "total": all_apps.count(),
            "pending": all_apps.filter(status="Pending").count(),
            "accepted": all_apps.filter(status="Accepted").count(),
            "rejected": all_apps.filter(status="Rejected").count(),
        }
        if history_filter in {"Pending", "Accepted", "Rejected"}:
            all_apps = all_apps.filter(status=history_filter)
        applications = all_apps

    context = {
        "student": student,
        "view": view,
        "recommended_jobs": recommended_jobs,
        "applications": applications,
        "history_filter": history_filter,
        "history_counts": history_counts,
        "resume_form": ResumeForm(),
    }
    return render(request, "jobs/student_dashboard.html", context)


@login_required(role="student")
@require_POST
def upload_resume(request):
    student = current_student(request)
    form = ResumeForm(request.POST, request.FILES)
    if form.is_valid():
        student.resume_filename = form.cleaned_data["resume"]
        student.save(update_fields=["resume_filename"])
        messages.success(request, "Resume uploaded. Companies can now see it when you apply.")
    else:
        messages.error(request, " ".join(form.errors["resume"]))
    return redirect(f"{reverse('jobs:student_dashboard')}?view=profile")


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
    elif view == "history":
        jobs = Job.objects.filter(company=company).annotate(
            total_applicants=Count("applications"),
            pending_count=Count("applications", filter=Q(applications__status="Pending")),
            accepted_count=Count("applications", filter=Q(applications__status="Accepted")),
            rejected_count=Count("applications", filter=Q(applications__status="Rejected")),
        )
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
    if application.is_final:
        messages.error(request, "This application was already decided and its status cannot be changed.")
    elif status_val not in {"Accepted", "Rejected"}:
        messages.error(request, "Invalid application status")
    else:
        application.decide(status_val)
        messages.success(request, f"Application {status_val.lower()}.")
    return redirect(f"{reverse('jobs:company_dashboard')}?view=applicants")
