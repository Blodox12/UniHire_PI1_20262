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


import re

from django.core import mail
from django.urls import reverse

from .models import Student


class UsernameLoginTests(TestCase):
    def setUp(self):
        user = CustomUser.objects.create_user(
            email="ana@example.com", password="StrongPass123", role="student", username="Ana.Dev"
        )
        Student.objects.create(user=user, name="Ana", email="ana@example.com")

    def login(self, identifier, password="StrongPass123", role="student"):
        return self.client.post(
            reverse("accounts:login"), {"role": role, "identifier": identifier, "password": password}
        )

    def test_login_with_email(self):
        self.assertRedirects(self.login("ANA@example.com"), reverse("jobs:student_dashboard"))

    def test_login_with_username_ignoring_case(self):
        self.assertRedirects(self.login("ana.dev"), reverse("jobs:student_dashboard"))

    def test_wrong_password_or_role_fails(self):
        self.assertEqual(self.login("ana.dev", "wrong").status_code, 200)
        self.assertEqual(self.login("ana.dev", role="company").status_code, 200)

    def test_duplicate_username_is_rejected_ignoring_case(self):
        data = {
            "name": "Beto", "username": "ANA.DEV", "email": "beto@example.com", "password": "secret12",
            "university": "EAFIT", "career": "Economía", "semester": "3",
        }
        r = self.client.post(reverse("accounts:register_student"), data)
        self.assertContains(r, "already taken")
        self.assertFalse(CustomUser.objects.filter(email="beto@example.com").exists())
        data["username"] = "beto_99"
        self.client.post(reverse("accounts:register_student"), data)
        self.assertTrue(CustomUser.objects.filter(email="beto@example.com", username="beto_99").exists())

    def test_invalid_username_format(self):
        data = {
            "name": "Beto", "username": "a@b", "email": "beto@example.com", "password": "secret12",
            "university": "EAFIT", "career": "Economía", "semester": "3",
        }
        r = self.client.post(reverse("accounts:register_student"), data)
        self.assertContains(r, "3-30 characters")


class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user("ana@example.com", "OldPass12345", role="student")
        Student.objects.create(user=self.user, name="Ana", email="ana@example.com")

    def test_login_page_links_to_reset(self):
        self.assertContains(self.client.get(reverse("accounts:login")), reverse("accounts:password_reset"))

    def test_full_reset_flow(self):
        r = self.client.post(reverse("accounts:password_reset"), {"email": "ana@example.com"})
        self.assertRedirects(r, reverse("accounts:password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        link = re.search(r"http://testserver(\S+)", mail.outbox[0].body).group(1)
        r = self.client.get(link, follow=True)  # Django swaps the token for a session URL
        r = self.client.post(r.request["PATH_INFO"], {"new_password1": "BrandNewPass987", "new_password2": "BrandNewPass987"})
        self.assertRedirects(r, reverse("accounts:password_reset_complete"))
        r = self.client.post(
            reverse("accounts:login"), {"role": "student", "identifier": "ana@example.com", "password": "BrandNewPass987"}
        )
        self.assertRedirects(r, reverse("jobs:student_dashboard"))

    def test_unknown_email_does_not_reveal_or_send(self):
        r = self.client.post(reverse("accounts:password_reset"), {"email": "nobody@example.com"})
        self.assertRedirects(r, reverse("accounts:password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)
