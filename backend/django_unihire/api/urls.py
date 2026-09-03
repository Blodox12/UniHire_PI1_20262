from django.urls import path
from . import views

urlpatterns = [
    path("status", views.status),
    path("auth/register", views.register),
    path("auth/login", views.login),
    path("jobs", views.jobs_list),
    path("jobs/search", views.search_jobs),
    path("jobs/recommended", views.recommended_jobs),
    path("jobs/<int:job_id>", views.job_detail),
    path("jobs/create", views.create_job),
    path("applications", views.applications_dispatch),
    path("students/profile", views.students_profile_dispatch),
    path("companies/profile", views.companies_profile_dispatch),
    path("companies/jobs", views.company_jobs),
    path("applications/list", views.student_applications),
    path("applications/company", views.company_applicants),
    path("applications/<int:application_id>/status", views.update_application_status),
]
