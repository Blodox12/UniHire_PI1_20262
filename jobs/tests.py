import tempfile

from django.contrib.admin.sites import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase, override_settings
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
            {"role": "company", "identifier": "company@example.com", "password": self.password},
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
            {"company_name": "NewCo", "username": "newco", "email": "new@example.com", "password": self.password},
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
            {"role": "student", "identifier": "student@example.com", "password": self.password},
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


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ApplicationFlowTests(TestCase):
    def setUp(self):
        s_user = CustomUser.objects.create_user("s@example.com", "secret12", role="student")
        c_user = CustomUser.objects.create_user("c@example.com", "secret12", role="company")
        self.student = Student.objects.create(user=s_user, name="Ana", email="s@example.com")
        self.company = Company.objects.create(
            user=c_user, company_name="Acme", email="c@example.com", verification_status=Company.STATUS_APPROVED
        )
        self.job = Job.objects.create(company=self.company, title="Dev", description="d", required_skills="python", location="Medellin")
        self.application = Application.objects.create(student=self.student, job=self.job)

    def login(self, email):
        self.client.post(reverse("accounts:login"), {"role": "student" if email.startswith("s") else "company", "identifier": email, "password": "secret12"})

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


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ImprovementTests(TestCase):
    def setUp(self):
        s_user = CustomUser.objects.create_user("s@example.com", "secret12", role="student")
        c_user = CustomUser.objects.create_user("c@example.com", "secret12", role="company")
        self.student = Student.objects.create(user=s_user, name="Ana", email="s@example.com", career="Ingeniería de Sistemas")
        self.company = Company.objects.create(
            user=c_user, company_name="Acme", email="c@example.com", verification_status=Company.STATUS_APPROVED
        )
        self.job = Job.objects.create(company=self.company, title="Dev", description="d", required_skills="python", location="Medellin")
        self.job2 = Job.objects.create(company=self.company, title="QA", description="d", required_skills="qa", location="Medellin")

    def login(self, role):
        email = "s@example.com" if role == "student" else "c@example.com"
        self.client.post(reverse("accounts:login"), {"role": role, "identifier": email, "password": "secret12"})

    def test_apply_without_resume_warns_and_with_resume_snapshots(self):
        self.login("student")
        r = self.client.post(reverse("jobs:apply_to_job", args=[self.job.id]), follow=True)
        self.assertContains(r, "applied without a resume")
        self.student.resume_filename.save("cv.pdf", SimpleUploadedFile("cv.pdf", b"%PDF-1.4 v1"))
        self.client.post(reverse("jobs:apply_to_job", args=[self.job2.id]))
        app = Application.objects.get(job=self.job2)
        self.assertTrue(app.resume)
        # a later upload does not change the resume sent with the application
        self.student.resume_filename.save("cv2.pdf", SimpleUploadedFile("cv2.pdf", b"%PDF-1.4 v2"))
        app.refresh_from_db()
        with app.resume.open("rb") as f:
            self.assertEqual(f.read(), b"%PDF-1.4 v1")

    def test_decision_note_email_and_new_marker(self):
        from django.core import mail

        app = Application.objects.create(student=self.student, job=self.job)
        self.login("company")
        self.client.post(
            reverse("jobs:update_application_status", args=[app.id]),
            {"status": "Rejected", "decision_note": "Need more experience"},
        )
        app.refresh_from_db()
        self.assertEqual(app.decision_note, "Need more experience")
        self.assertFalse(app.seen_by_student)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Need more experience", mail.outbox[0].body)
        # second attempt is ignored: no extra email
        self.client.post(reverse("jobs:update_application_status", args=[app.id]), {"status": "Accepted"})
        self.assertEqual(len(mail.outbox), 1)

        self.client.cookies.clear()
        self.login("student")
        r = self.client.get(reverse("jobs:student_dashboard") + "?view=history")
        self.assertContains(r, "NEW")
        self.assertContains(r, "Need more experience")
        app.refresh_from_db()
        self.assertTrue(app.seen_by_student)
        r = self.client.get(reverse("jobs:student_dashboard") + "?view=history")
        self.assertNotContains(r, "NEW")

    def test_applicant_filters_and_order(self):
        a1 = Application.objects.create(student=self.student, job=self.job)
        a1.decide("Accepted")
        s2 = Student.objects.create(name="Beto", email="b@example.com")
        Application.objects.create(student=s2, job=self.job2)
        self.login("company")
        url = reverse("jobs:company_dashboard")
        r = self.client.get(url + "?view=applicants")
        names = [a.student.name for a in r.context["applicants"]]
        self.assertEqual(names, ["Beto", "Ana"])  # pending first
        r = self.client.get(url + f"?view=applicants&job={self.job.id}")
        self.assertEqual([a.student.name for a in r.context["applicants"]], ["Ana"])
        r = self.client.get(url + "?view=applicants&status=Pending")
        self.assertEqual([a.student.name for a in r.context["applicants"]], ["Beto"])

    def test_history_search(self):
        Application.objects.create(student=self.student, job=self.job)
        Application.objects.create(student=self.student, job=self.job2)
        self.login("student")
        r = self.client.get(reverse("jobs:student_dashboard") + "?view=history&q=QA")
        self.assertEqual([a.job.title for a in r.context["applications"]], ["QA"])
