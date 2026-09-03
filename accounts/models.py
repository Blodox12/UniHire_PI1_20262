from django.db import models


class Student(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    university = models.CharField(max_length=150, blank=True)
    career = models.CharField(max_length=150, blank=True)
    semester = models.CharField(max_length=10, blank=True)
    skills = models.CharField(max_length=500, blank=True)
    certifications = models.CharField(max_length=500, blank=True)
    resume_filename = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Company(models.Model):
    company_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name
