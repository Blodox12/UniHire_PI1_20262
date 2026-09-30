from django.contrib.auth import authenticate
from django.test import TestCase

from .models import CustomUser


class AuthPasswordTests(TestCase):
    def test_create_user_stores_hashed_password(self):
        user = CustomUser.objects.create_user(
            email="student@example.com",
            password="StrongPass123",
            role="student",
        )

        self.assertNotEqual(user.password, "StrongPass123")
        self.assertTrue(user.check_password("StrongPass123"))

    def test_authenticate_works_with_email(self):
        CustomUser.objects.create_user(
            email="company@example.com",
            password="StrongPass456",
            role="company",
        )

        user = authenticate(email="company@example.com", password="StrongPass456")

        self.assertIsNotNone(user)
        self.assertEqual(user.email, "company@example.com")
        self.assertEqual(user.role, "company")
