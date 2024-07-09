from django.contrib.auth import get_user_model
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = get_user_model().objects.create_user(
            username="testuser1", email="testuser1@test.com", password="testpassword1"
        )
        self.user2 = get_user_model().objects.create_user(
            username="testuser2", email="testuser2@test.com", password="testpassword2"
        )

        self.client.force_authenticate(user=self.user1)
        self.client.force_authenticate(user=self.user1)

    def test_api(self):
        # Define the URL and data
        url = reverse("profile")
        data = {"key": "value"}

        # Make a POST request to the API
        response = self.client.post(url, data, format="json")

        # Check the status code and response data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, data)

    def test_api_get(self):
        # Define the URL
        url = "/profile/2/"

        # Make a GET request to the API
        response = self.client.get(url)

        # Check the status code and response data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)

        expected_data = {
            "username": "testuser2",
            "email": "testuser2@test.com",
        }
        self.assertEqual(response.data, expected_data)
