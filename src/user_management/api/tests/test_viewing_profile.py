import uuid

from api.models import CustomUser
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from friends.models import FriendList


# is_self, friend, stranger logic potentially ONLY for the SEARCH ENDPOINT
class CustomUserProfileTest(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = CustomUser.objects.create(user_id=uuid.uuid4(), displayname='TestUser1', online=False)
        self.user2 = CustomUser.objects.create(user_id=uuid.uuid4(), displayname='TestUser2', online=True)
        self.user3 = CustomUser.objects.create(user_id=uuid.uuid4(), displayname='TestUser3', online=True)

        # Create FriendList instances
        FriendList.objects.create(user=self.user1)
        FriendList.objects.create(user=self.user2)
        FriendList.objects.create(user=self.user3)

        # Add user2 as a friend of user1
        self.user1.friend_list.friends.add(self.user2)

        # Initialize the test client
        self.client = Client()
        self.client.force_login(self.user1)

    def test_view_own_profile(self):
        # Simulate logging in as user1

        # Access user1's profile
        response = self.client.get(reverse('custom_user_profile', args=[self.user1.displayname]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['is_self'])
