from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase
from django.urls import reverse

from accounts.admin import CompanyAdmin
from accounts.models import Company, CustomUser, Student

from .models import Application, Job


class CompanyApprovalTests(TestCase):
    password = "StrongPass123"

    def setUp(self):
        self.company_user = CustomUser.objects.create_user(
            email="company@example.com", password=self.password, role="company"
        )
        self.company = Company.objects.create(
            user=self.company_user, company_name="Acme", email="company@example.com"
        )
        student_user = CustomUser.objects.create_user(
            email="student@example.com", password=self.password, role="student"
        )
        self.student = Student.objects.create(
            user=student_user, name="Ana", email="student@example.com"
        )

    def login_company(self):
        self.client.post(
            reverse("accounts:login"),
            {"role": "company", "email": "company@example.com", "password": self.password},
        )

    def create_job_data(self):
        return {
            "title": "Intern",
            "description": "Help us",
            "required_skills": "python",
            "location": "Medellin",
            "job_type": "Remote",
        }

    def test_new_company_registers_as_pending(self):
        self.client.post(
            reverse("accounts:register_company"),
            {"company_name": "NewCo", "email": "new@example.com", "password": self.password},
        )
        company = Company.objects.get(email="new@example.com")
        self.assertEqual(company.verification_status, Company.STATUS_PENDING)

    def test_pending_company_cannot_create_job(self):
        self.login_company()
        response = self.client.post(reverse("jobs:create_job"), self.create_job_data())
        self.assertRedirects(response, reverse("jobs:company_dashboard"))
        self.assertFalse(Job.objects.exists())

    def test_pending_company_cannot_see_applicants(self):
        job = Job.objects.create(company=self.company, title="Intern", description="x",
                                 required_skills="python", location="Medellin")
        Application.objects.create(student=self.student, job=job)
        self.login_company()
        response = self.client.get(reverse("jobs:company_dashboard") + "?view=applicants")
        self.assertEqual(response.context["view"], "jobs")
        self.assertNotContains(response, "Ana")

    def test_rejected_company_cannot_create_job(self):
        self.company.verification_status = Company.STATUS_REJECTED
        self.company.save()
        self.login_company()
        self.client.post(reverse("jobs:create_job"), self.create_job_data())
        self.assertFalse(Job.objects.exists())

    def test_approved_company_can_create_job(self):
        self.company.verification_status = Company.STATUS_APPROVED
        self.company.save()
        self.login_company()
        self.client.post(reverse("jobs:create_job"), self.create_job_data())
        self.assertTrue(Job.objects.filter(company=self.company).exists())

    def test_jobs_of_unapproved_companies_are_hidden(self):
        job = Job.objects.create(company=self.company, title="Hidden job", description="x",
                                 required_skills="python", location="Medellin")
        self.assertNotContains(self.client.get(reverse("jobs:jobs")), "Hidden job")
        self.assertEqual(self.client.get(reverse("jobs:job_detail", args=[job.id])).status_code, 404)

    def test_student_cannot_access_company_views(self):
        self.client.post(
            reverse("accounts:login"),
            {"role": "student", "email": "student@example.com", "password": self.password},
        )
        response = self.client.get(reverse("jobs:create_job"))
        self.assertRedirects(response, reverse("jobs:student_dashboard"))

    def test_admin_approve_action_records_reviewer(self):
        admin_user = CustomUser.objects.create_superuser(email="admin@example.com", password=self.password)
        request = RequestFactory().post("/admin/")
        request.user = admin_user
        model_admin = CompanyAdmin(Company, AdminSite())
        model_admin.message_user = lambda *args, **kwargs: None
        model_admin.approve_companies(request, Company.objects.filter(id=self.company.id))

        self.company.refresh_from_db()
        self.assertEqual(self.company.verification_status, Company.STATUS_APPROVED)
        self.assertEqual(self.company.reviewed_by, admin_user)
        self.assertIsNotNone(self.company.reviewed_at)
