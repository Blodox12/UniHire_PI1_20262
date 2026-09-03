from django.contrib import admin

from .models import Application, Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "company", "location", "job_type", "created_at")
    list_filter = ("job_type",)
    search_fields = ("title", "required_skills", "location")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "job", "status", "applied_at")
    list_filter = ("status",)
