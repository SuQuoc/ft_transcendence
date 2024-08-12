import uuid

from django.urls import reverse
from rest_framework.test import APITestCase
from utils_jwt import generate_token

class TestSetUp(APITestCase):
    def setUp(self):
        self.user_id = str(uuid.uuid4())
        self.displayname = "Test API"
        self.data = {
            "user_id": self.user_id,
            "displayname": self.displayname,
        }
        self.url = reverse("user-creation")

        self.access_token = generate_token(self.user_id)
        self.headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.access_token}",
        }
        self.access_token

    def post(self):
        return self.client.post(self.url, self.data, format="json", secure=True, **self.headers)
