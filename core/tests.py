from django.test import TestCase, Client
from django.urls import reverse

from rest_framework.test import APIClient
from django.contrib.auth.models import User

class BasicSiteTests(TestCase):
    """
    Basic smoke tests to check the main pages of the site.
    """

    def setUp(self):
        """Initialize the test client before each test"""
        self.client = Client()

    def test_homepage_returns_200(self):
        """
        Verify that the home page returns a status of 200.
        """
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        """
        Verify that the login page opens successfully.
        """
        response = self.client.get(reverse("login-page"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")

    def test_register_page_loads(self):
        """
        Verify that the registration page opens successfully.
        """
        response = self.client.get(reverse("register-page"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Register")

    def test_profile_redirects_if_not_logged_in(self):
        """
        Checking that a non-logged-in user receives a redirect from the profile page.
        """
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login-required/", response.url)


# API

class APITestCase(TestCase):
    """
    Tests for registration, login, and text generation APIs.
    """

    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/register/"
        self.login_url = "/api/login/"
        self.generate_url = "/api/generate/"

        self.user_data = {
            "username": "apitestuser",
            "password": "securepass123",
            "email": "apitest@example.com"
        }

    def test_user_registration(self):
        """
        Checks that the user can register via the API.
        """
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, 201)

    def test_token_login(self):
        """
        Verify that the user can obtain a token.
        """
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.login_url, {
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())

    def test_generate_with_auth(self):
        """
        Verifies that an authorized user can generate text.
        """
        User.objects.create_user(**self.user_data)
        token_res = self.client.post(self.login_url, {
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        })
        access_token = token_res.json()["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.post(self.generate_url, {"text": "Hello, GPT!"})
        self.assertEqual(response.status_code, 201)
        self.assertIn("ai_response", response.json())