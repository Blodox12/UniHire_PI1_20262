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


if __name__ == "__main__":
    unittest.main()
