import os
import tempfile
import unittest
from pathlib import Path

os.environ["JWT_SECRET"] = "test-secret"

import app as backend


class ApiFlowTest(unittest.TestCase):
    def setUp(self):
        self.database = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.database.close()
        backend.DATABASE_PATH = Path(self.database.name)
        self.client = backend.app.test_client()
        with backend.app.app_context():
            backend.initialize_database()

    def tearDown(self):
        Path(self.database.name).unlink(missing_ok=True)

    def test_student_registration_login_and_application_flow(self):
        response = self.client.post("/api/auth/register", json={
            "role": "student", "name": "Ana", "email": "ana@test.com",
            "password": "secret", "university": "Uni", "career": "Software",
            "semester": "6", "skills": "Python, SQL"
        })
        self.assertEqual(response.status_code, 201)
        response = self.client.post("/api/auth/login", json={
            "role": "student", "email": "ana@test.com", "password": "secret"
        })
        self.assertEqual(response.status_code, 200)
        token = response.get_json()["token"]
        self.assertEqual(self.client.get("/api/status").get_json()["status"], "ok")
        self.assertEqual(self.client.get("/api/jobs").get_json()["jobs"], [])
        profile_headers = {"Authorization": f"Bearer {token}"}
        self.assertEqual(self.client.get("/api/students/profile", headers=profile_headers).status_code, 200)
        response = self.client.put("/api/students/profile", headers=profile_headers, json={
            "name": "Ana Updated", "university": "Uni", "career": "Software",
            "semester": "7", "skills": "Python, Flask"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["student"]["name"], "Ana Updated")

    def test_job_detail_endpoint(self):
        self.client.post("/api/auth/register", json={
            "role": "company", "companyName": "TechCorp", "email": "tech@test.com", "password": "secret"
        })
        login = self.client.post("/api/auth/login", json={
            "role": "company", "email": "tech@test.com", "password": "secret"
        })
        token = login.get_json()["token"]
        self.client.post("/api/jobs", headers={"Authorization": f"Bearer {token}"}, json={
            "title": "Senior Python Dev", "description": "Lead backend team",
            "required_skills": "Python, Leadership", "location": "NYC", "job_type": "On-site"
        })
        job_id = self.client.get("/api/jobs").get_json()["jobs"][0]["id"]
        response = self.client.get(f"/api/jobs/{job_id}")
        self.assertEqual(response.status_code, 200)
        job = response.get_json()["job"]
        self.assertEqual(job["title"], "Senior Python Dev")
        self.assertEqual(job["company_name"], "TechCorp")

    def test_job_search_and_filtering(self):
        self.client.post("/api/auth/register", json={
            "role": "company", "companyName": "DevCorp", "email": "dev@test.com", "password": "secret"
        })
        login = self.client.post("/api/auth/login", json={
            "role": "company", "email": "dev@test.com", "password": "secret"
        })
        token = login.get_json()["token"]
        self.client.post("/api/jobs", headers={"Authorization": f"Bearer {token}"}, json={
            "title": "Python Backend Dev", "description": "Build APIs with Flask",
            "required_skills": "Python, Flask, PostgreSQL", "location": "New York", "job_type": "Remote"
        })
        self.client.post("/api/jobs", headers={"Authorization": f"Bearer {token}"}, json={
            "title": "React Frontend Dev", "description": "Build web interfaces",
            "required_skills": "JavaScript, React", "location": "San Francisco", "job_type": "On-site"
        })
        response = self.client.get("/api/jobs/search?q=Python")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["count"], 1)
        response = self.client.get("/api/jobs/search?job_type=Remote")
        self.assertEqual(response.get_json()["count"], 1)
        response = self.client.get("/api/jobs/search?location=San")
        self.assertEqual(response.get_json()["count"], 1)
        response = self.client.get("/api/jobs/search")
        self.assertEqual(response.get_json()["count"], 2)

    def test_company_registration_and_duplicate_email(self):
        response = self.client.post("/api/auth/register", json={
            "role": "company", "companyName": "Acme", "email": "ACME@TEST.COM",
            "password": "secret"
        })
        self.assertEqual(response.status_code, 201)
        response = self.client.post("/api/auth/login", json={
            "role": "company", "email": "acme@test.com", "password": "secret"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["user"]["name"], "Acme")
        response = self.client.post("/api/auth/register", json={
            "role": "student", "name": "Another", "email": "acme@test.com",
            "password": "secret", "university": "Uni", "career": "Design", "semester": "2"
        })
        self.assertEqual(response.status_code, 400)

    def test_registration_rejects_weak_password_and_invalid_email(self):
        response = self.client.post("/api/auth/register", json={
            "role": "company", "companyName": "Acme", "email": "invalid",
            "password": "123"
        })
        self.assertEqual(response.status_code, 400)

    def test_company_can_create_update_and_delete_own_job(self):
        self.client.post("/api/auth/register", json={
            "role": "company", "companyName": "Acme", "email": "acme@test.com", "password": "secret"
        })
        login = self.client.post("/api/auth/login", json={
            "role": "company", "email": " ACME@TEST.COM ", "password": "secret"
        })
        token = login.get_json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post("/api/jobs", headers=headers, json={
            "title": "Junior Python Developer", "description": "Build APIs",
            "required_skills": "Python, SQL", "location": "Remote", "job_type": "Remote"
        })
        self.assertEqual(response.status_code, 201)
        job_id = self.client.get("/api/companies/jobs", headers=headers).get_json()["jobs"][0]["id"]
        response = self.client.put(f"/api/jobs/{job_id}", headers=headers, json={
            "title": "Python Developer", "description": "Build Flask APIs",
            "required_skills": "Python, Flask", "location": "Bogota", "job_type": "Hybrid"
        })
        self.assertEqual(response.status_code, 200)
        updated = self.client.get("/api/jobs").get_json()["jobs"][0]
        self.assertEqual(updated["title"], "Python Developer")
        self.assertEqual(self.client.delete(f"/api/jobs/{job_id}", headers=headers).status_code, 200)
        self.assertEqual(self.client.get("/api/jobs").get_json()["jobs"], [])

    def test_student_can_apply_to_job_and_view_applications(self):
        self.client.post("/api/auth/register", json={
            "role": "student", "name": "John", "university": "MIT", "career": "CS",
            "semester": 4, "email": "student@test.com", "password": "secret123"
        })
        student_login = self.client.post("/api/auth/login", json={
            "role": "student", "email": "student@test.com", "password": "secret123"
        })
        student_token = student_login.get_json()["token"]
        self.client.post("/api/auth/register", json={
            "role": "company", "companyName": "TechCo", "email": "company@test.com", "password": "secret123"
        })
        company_login = self.client.post("/api/auth/login", json={
            "role": "company", "email": "company@test.com", "password": "secret123"
        })
        company_token = company_login.get_json()["token"]
        job_response = self.client.post("/api/jobs", headers={"Authorization": f"Bearer {company_token}"}, json={
            "title": "Software Engineer", "description": "Build great software",
            "required_skills": "Python, JavaScript", "location": "San Francisco", "job_type": "Remote"
        })
        job_id = job_response.get_json()["job"]["id"]
        apply_response = self.client.post("/api/applications", headers={"Authorization": f"Bearer {student_token}"}, json={"jobId": job_id})
        self.assertEqual(apply_response.status_code, 201)
        apps_response = self.client.get("/api/applications", headers={"Authorization": f"Bearer {student_token}"})
        self.assertEqual(len(apps_response.get_json()["applications"]), 1)
        app = apps_response.get_json()["applications"][0]
        self.assertEqual(app["job_id"], job_id)
        self.assertEqual(app["status"], "Pending")
        company_apps = self.client.get("/api/applications/company", headers={"Authorization": f"Bearer {company_token}"})
        self.assertEqual(len(company_apps.get_json()["applicants"]), 1)
        duplicate_response = self.client.post("/api/applications", headers={"Authorization": f"Bearer {student_token}"}, json={"jobId": job_id})
        self.assertEqual(duplicate_response.status_code, 400)
        self.assertIn("already applied", duplicate_response.get_json()["message"].lower())



if __name__ == "__main__":
    unittest.main()
