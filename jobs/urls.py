from django.urls import path

from . import views

app_name = "jobs"

urlpatterns = [
    path("jobs/", views.jobs_view, name="jobs"),
    path("jobs/create/", views.create_job, name="create_job"),
    path("jobs/<int:job_id>/", views.job_detail, name="job_detail"),
    path("jobs/<int:job_id>/apply/", views.apply_to_job, name="apply_to_job"),
    path("jobs/<int:job_id>/edit/", views.edit_job, name="edit_job"),
    path("jobs/<int:job_id>/delete/", views.delete_job, name="delete_job"),

    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),
    path("company/dashboard/", views.company_dashboard, name="company_dashboard"),
    path(
        "applications/<int:application_id>/status/",
        views.update_application_status,
        name="update_application_status",
    ),
]
