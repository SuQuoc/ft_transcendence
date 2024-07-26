import json
import uuid

import api
from api.models import CustomUser
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


# DO I HAVE TO BE LOGGED IN
class TestUserCreation(APITestCase):
    def setUp(self):
        self.user_id = str(uuid.uuid4())
        self.displayname = "Test API"
        self.data = {
            'user_id': self.user_id,
            "displayname": self.displayname,
        }
        self.url = reverse('user-creation')

    def test_no_uid(self):
        del self.data['user_id']  # This will remove the key 'user_id' and its value from self.data
        response = self.client.post(self.url, self.data, format="json", secure=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_displayname(self):
        del self.data['displayname']  #
        response = self.client.post(self.url, self.data, format="json", secure=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # print(response.data)

    def test_invalid_uid(self):
        self.data['user_id'] = "invalid user id"
        response = self.client.post(self.url, self.data, format="json", secure=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # print(response.data)

    def test_displayname_too_long(self):
        self.data['displayname'] = "displayname too long ggggggggggggggggggggggggggg"
        response = self.client.post(self.url, self.data, format="json", secure=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # print(response.data)

    def test_wrong_key_name(self):
        del self.data["user_id"]
        self.data['iser_id'] = self.user_id
        response = self.client.post(self.url, self.data, format="json", secure=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_data(self):
        data = {}
        response = self.client.post(self.url, data, format="json", secure=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate(self):
        response = self.client.post(self.url, self.data, format="json", secure=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.url, self.data, format="json", secure=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(CustomUser.objects.count(), 1)
        # print(response.data)

    # Succesful api call
    def test_success(self):
        # print(f"q: uuid: {self.user_id}, data.user_id {self.data['user_id']}")
        response = self.client.post(self.url, self.data, format="json", secure=True)
        # print(f"q: RESPONSE: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().displayname, self.data["displayname"])
        self.assertEqual(str(CustomUser.objects.get().user_id), self.data["user_id"])

    def test_additional_unrequired_data(self):
        self.data['iser_id'] = "unrequired_data"
        response = self.client.post(self.url, self.data, format="json", secure=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# class TestFriendRequest(APITestCase):
#     def setUp(self):
#         self.user1 = CustomUser.objects.create(user_id=uuid.uuid4(), displayname='tester1')
#         self.user2 = CustomUser.objects.create(user_id=uuid.uuid4(), displayname='tester1')
#         self.data = {}
#
#     def test_success(self):
#         response = self.client.post(self.url, self.data, format="json", secure=True)
