from django.urls import path
from . import views

urlpatterns = [
    path("status", views.status),
    path("auth/register", views.register),
    path("auth/login", views.login),
    path("jobs", views.jobs_list),
    path("jobs/<int:job_id>", views.job_detail),
    path("jobs/create", views.create_job),
    path("applications", views.apply_to_job),
]
