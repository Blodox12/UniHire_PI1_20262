from django.contrib import admin
from django.utils import timezone

from .models import Company, Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "university", "career", "semester")
    search_fields = ("name", "email")


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "company_name", "email", "verification_status", "reviewed_by", "reviewed_at")
    list_filter = ("verification_status",)
    search_fields = ("company_name", "email")
    readonly_fields = ("reviewed_by", "reviewed_at", "created_at")
    actions = ("approve_companies", "reject_companies")

    def _review(self, request, queryset, status):
        return queryset.update(
            verification_status=status,
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )

    @admin.action(description="Approve selected companies")
    def approve_companies(self, request, queryset):
        updated = self._review(request, queryset, Company.STATUS_APPROVED)
        self.message_user(request, f"{updated} company(ies) approved.")

    @admin.action(description="Reject selected companies")
    def reject_companies(self, request, queryset):
        updated = self._review(request, queryset, Company.STATUS_REJECTED)
        self.message_user(request, f"{updated} company(ies) rejected. You can add a reason by editing each company.")

    def save_model(self, request, obj, form, change):
        # Record the reviewer when the status is changed from the edit form.
        if change and "verification_status" in form.changed_data:
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)
