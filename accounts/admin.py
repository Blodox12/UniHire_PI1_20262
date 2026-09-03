from django.contrib import admin

from .models import Company, Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "university", "career", "semester")
    search_fields = ("name", "email")


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "company_name", "email")
    search_fields = ("company_name", "email")
