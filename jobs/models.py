from django.db import models
from django.utils import timezone


class Job(models.Model):
    JOB_TYPES = [
        ("Remote", "Remote"),
        ("Hybrid", "Hybrid"),
        ("On-site", "On-site"),
    ]

    company = models.ForeignKey(
        "accounts.Company", on_delete=models.CASCADE, related_name="jobs"
    )
    title = models.CharField(max_length=120)
    description = models.TextField(max_length=2000)
    required_skills = models.CharField(max_length=500)
    location = models.CharField(max_length=150)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default="Remote")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.title

    def skills_list(self):
        return [item.strip() for item in (self.required_skills or "").split(",") if item.strip()]


class Application(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
    ]

    student = models.ForeignKey(
        "accounts.Student", on_delete=models.CASCADE, related_name="applications"
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    applied_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "job")
        ordering = ["-id"]

    def __str__(self):
        return f"{self.student} -> {self.job} ({self.status})"

    @property
    def is_final(self):
        """Accepted/Rejected applications are final and can no longer change."""
        return self.status != "Pending"

    def decide(self, status):
        """Set a final status once. Returns False if it was already decided."""
        if self.is_final or status not in ("Accepted", "Rejected"):
            return False
        self.status = status
        self.decided_at = timezone.now()
        self.save(update_fields=["status", "decided_at"])
        return True
