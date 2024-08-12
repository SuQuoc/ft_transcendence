import uuid

from api.models import CustomUser
from django.test import TestCase
from django.urls import reverse
from friends.models import FriendList
from utils_jwt import generate_token


# is_self, friend, stranger logic potentially ONLY for the SEARCH ENDPOINT
class CustomUserProfileTest(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create(user_id=uuid.uuid4(), displayname='TestUser1', online=False)
        self.friend = CustomUser.objects.create(user_id=uuid.uuid4(), displayname='Friend', online=True)
        self.stranger = CustomUser.objects.create(user_id=uuid.uuid4(), displayname='Stranger', online=True)


        self.user1.friend_list.friends.add(self.friend)  # test independent on the friend-request api

        self.access_token = generate_token(self.user1.user_id)
        self.headers = {
            'HTTP_AUTHORIZATION': f'Bearer {self.access_token}',
        }
        # print(f"\nJWT: {self.access_token}")

    def get(self):
        return self.client.get(self.url, secure=True, **self.headers)  # Ensure the request is made over HTTPS or else u get 301 Message

    def test_view_own_profile(self):
        self.url = reverse('profile', args=[self.user1.displayname])
        response = self.get()
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['is_self'])
        self.assertFalse(response.json()['is_friend'])
        self.assertFalse(response.json()['is_stranger'])

    def test_view_friends_profile(self):
        self.url = reverse('profile', args=[self.friend.displayname])
        response = self.get()
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['is_self'])
        self.assertTrue(response.json()['is_friend'])
        self.assertFalse(response.json()['is_stranger'])

    def test_view_strangers_profile(self):
        self.url = reverse('profile', args=[self.stranger.displayname])
        response = self.get()
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['is_self'])
        self.assertFalse(response.json()['is_friend'])
        self.assertTrue(response.json()['is_stranger'])
