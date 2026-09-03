from django.db import models


class Student(models.Model):
    name = models.TextField()
    email = models.TextField(unique=True)
    password = models.TextField()
    university = models.TextField(blank=True)
    career = models.TextField(blank=True)
    semester = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    resume_filename = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Company(models.Model):
    company_name = models.TextField()
    email = models.TextField(unique=True)
    password = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.TextField()
    description = models.TextField()
    required_skills = models.TextField()
    location = models.TextField()
    job_type = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Application(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    status = models.TextField(default="Pending")
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "job")
