import uuid

from api.models import CustomUser
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from friends.models import FriendList
from rest_framework_simplejwt.tokens import RefreshToken
from utils_jwt import generate_token

# is_self, friend, stranger logic potentially ONLY for the SEARCH ENDPOINT
class CustomUserProfileTest(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create(user_id=uuid.uuid4(), displayname='TestUser1', online=False)
        self.user2 = CustomUser.objects.create(user_id=uuid.uuid4(), displayname='TestUser2', online=True)
        self.user3 = CustomUser.objects.create(user_id=uuid.uuid4(), displayname='TestUser3', online=True)

        # Create FriendList instances, since it's only done for u when the api is used
        FriendList.objects.create(user=self.user1)
        FriendList.objects.create(user=self.user2)
        FriendList.objects.create(user=self.user3)

        self.user1.friend_list.friends.add(self.user2)

        # Initialize the test client
        self.client = Client()

        self.access_token = generate_token(self.user1.user_id)
        # print(f"\nJWT: {self.access_token}")

    def test_view_own_profile(self):
        url = reverse('profile', args=[self.user1.displayname])
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {self.access_token}', secure=True)  # Ensure the request is made over HTTPS or else u get 301 Message
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['is_self'])
        self.assertFalse(response.json()['is_friend'])
        self.assertFalse(response.json()['is_stranger'])
