import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import Company, CustomUser, Student

from .models import Application, Job


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ApplicationFlowTests(TestCase):
    def setUp(self):
        s_user = CustomUser.objects.create_user("s@example.com", "secret12", role="student")
        c_user = CustomUser.objects.create_user("c@example.com", "secret12", role="company")
        self.student = Student.objects.create(user=s_user, name="Ana", email="s@example.com")
        self.company = Company.objects.create(user=c_user, company_name="Acme", email="c@example.com")
        self.job = Job.objects.create(company=self.company, title="Dev", description="d", required_skills="python", location="Medellin")
        self.application = Application.objects.create(student=self.student, job=self.job)

    def login(self, email):
        self.client.post(reverse("accounts:login"), {"role": "student" if email.startswith("s") else "company", "email": email, "password": "secret12"})

    def test_decision_is_final(self):
        self.login("c@example.com")
        url = reverse("jobs:update_application_status", args=[self.application.id])
        self.client.post(url, {"status": "Accepted"})
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "Accepted")
        self.assertIsNotNone(self.application.decided_at)
        self.client.post(url, {"status": "Rejected"})
        self.client.post(url, {"status": "Pending"})
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "Accepted")

    def test_resume_upload_accepts_only_real_pdf(self):
        self.login("s@example.com")
        url = reverse("jobs:upload_resume")
        self.client.post(url, {"resume": SimpleUploadedFile("cv.pdf", b"not a pdf")})
        self.student.refresh_from_db()
        self.assertFalse(self.student.resume_filename)
        self.client.post(url, {"resume": SimpleUploadedFile("cv.txt", b"%PDF-1.4")})
        self.student.refresh_from_db()
        self.assertFalse(self.student.resume_filename)
        self.client.post(url, {"resume": SimpleUploadedFile("cv.pdf", b"%PDF-1.4 data")})
        self.student.refresh_from_db()
        self.assertTrue(self.student.resume_filename)

    def test_history_views_render(self):
        self.application.decide("Rejected")
        self.login("s@example.com")
        r = self.client.get(reverse("jobs:student_dashboard") + "?view=history&status=Rejected")
        self.assertContains(r, "Dev")
        self.client.cookies.clear()
        self.login("c@example.com")
        r = self.client.get(reverse("jobs:company_dashboard") + "?view=history")
        self.assertContains(r, "1 rejected")
        r = self.client.get(reverse("jobs:company_dashboard") + "?view=applicants")
        self.assertNotContains(r, "Accept</button>")
