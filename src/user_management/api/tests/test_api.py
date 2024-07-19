from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import CustomUser

class TestProfile(APITestCase):
    def test_create_profile(self):
        url = reverse("profile-list")
        data = {"displayname": "Testing profile creation api"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().displayname, 'Testing profile creation api')


