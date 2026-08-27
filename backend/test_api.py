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
        self.assertEqual(self.client.get("/api/students/profile", headers={"Authorization": f"Bearer {token}"}).status_code, 200)


if __name__ == "__main__":
    unittest.main()
