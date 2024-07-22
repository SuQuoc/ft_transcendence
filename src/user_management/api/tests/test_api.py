import uuid

import api
from api.models import CustomUser
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestProfile(APITestCase):
    user_id = str(uuid.uuid4())
    displayname = "Test API"
    data = {
        "user_id": user_id,
        "displayname": displayname,
    }

    url = reverse('user-creation')
    print_response = False

    def fillCorrectUserData(self):
        self.data = {
            "user_id": self.user_id,
            "displayname": self.displayname,
        }

    def test_user_creation_no_uid(self):
        del self.data['user_id']  # This will remove the key 'user_id' and its value from self.data
        response = self.client.post(self.url, self.data, format="json", secure=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.fillCorrectUserData()

    def test_user_creation_no_displayname(self):
        del self.data['displayname']  #
        response = self.client.post(self.url, self.data, format="json", secure=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.fillCorrectUserData()

    def test_user_creation_wrong_key_name(self):
        del self.data["user_id"]
        self.data['iser_id'] = self.user_id
        response = self.client.post(self.url, self.data, format="json", secure=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.fillCorrectUserData()

    def test_user_creation_no_data(self):
        data = {}
        response = self.client.post(self.url, data, format="json", secure=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Succesful api call
    def test_user_creation(self):
        self.fillCorrectUserData()
        response = self.client.post(self.url, self.data, format="json", secure=True)
        print(f"q: RESPONSE: {response.data}")

        # import pdb
        # pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().displayname, self.data["displayname"])
        self.assertEqual(CustomUser.objects.get().user_id, self.data["user_id"])

    def test_user_creation_additional_unrequired_data(self):
        self.fillCorrectUserData()
        self.data['iser_id'] = "unrequired_data"
        response = self.client.post(self.url, self.data, format="json", secure=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
