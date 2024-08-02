import json
import uuid

from api.models import CustomUser
from django.db import connection
from django.test import TestCase
from django.urls import reverse
from friends.models import FriendList
from friends.models import FriendRequest
from utils_jwt import generate_token


class FriendRequestTest(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create(user_id=uuid.uuid4(), displayname="TestUser1", online=False)
        self.friend = CustomUser.objects.create(user_id=uuid.uuid4(), displayname="Friend", online=True)
        self.stranger = CustomUser.objects.create(user_id=uuid.uuid4(), displayname="Stranger", online=True)

        # Create FriendList instances, since it"s only done for u when the api is used
        FriendList.objects.create(user=self.user1)
        FriendList.objects.create(user=self.friend)
        FriendList.objects.create(user=self.stranger)

        self.user1.friend_list.addFriend(self.friend)  # test independent of the "send-friend-request" api

        self.data = {"receiver": "SET THIS IN EACH TEST FUNCTION"}

        self.data_f_request = {"friendRequestId": "1"}

        self.url = reverse("send-friend-request")
        self.url_acc = reverse("acc-friend-request")
        self.url_dec = reverse("dec-friend-request")

        self.access_token = generate_token(self.user1.user_id)
        self.headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.access_token}",
        }

        # to reset the id to start with 1 for every test method,
        # if not done the id's will auto increment even though theres no other friendRequest in table
        # TLDR: one friend request in table with id of 2
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE friends_friendrequest RESTART IDENTITY CASCADE;")

    def tearDown(self):
        # Clean up after each test
        FriendRequest.objects.all().delete()
        CustomUser.objects.all().delete()

    def post(self):
        return self.client.post(self.url, data=self.data, content_type="application/json", format="json", secure=True, **self.headers)

    def test_sending_to_myself(self):
        self.data["receiver"] = self.user1.displayname
        response = self.post()
        response_json = response.json()
        # print(response)
        # print(response_json)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json["error"], "You can't send a friend request to yourself")

    def test_sending_to_friend(self):
        self.data["receiver"] = self.friend.displayname
        response = self.post()
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json["error"], "You are best buds")

    def test_sending_to_stranger(self):
        self.data["receiver"] = self.stranger.displayname
        response = self.post()
        response_json = response.json()
        count = FriendRequest.objects.filter(sender=self.user1, receiver=self.stranger, status=FriendRequest.PENDING).count()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(count, 1)
        self.assertEqual(response_json["message"], "friend request sent")

    def test_sending_to_stranger_twice(self):
        self.data["receiver"] = self.stranger.displayname
        response = self.post()
        response = self.post()
        response_json = response.json()
        count = FriendRequest.objects.filter(sender=self.user1, receiver=self.stranger, status=FriendRequest.PENDING).count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count, 1)
        self.assertEqual(response_json["message"], "friend request already sent, be patient")

    # Answering a friend request
    def test_accept_friend_request(self):
        self.test_sending_to_stranger()

        # setup for post to work correctly
        self.data = self.data_f_request
        self.url = self.url_acc
        self.headers["HTTP_AUTHORIZATION"] = f"Bearer {generate_token(self.stranger.user_id)}"

        response = self.post()
        response_json = response.json()
        count = FriendRequest.objects.filter(sender=self.user1, receiver=self.stranger, status=FriendRequest.ACCEPTED).count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count, 1)
        self.assertEqual(response_json["message"], "Friend request accepted")

    def test_decline_friend_request(self):
        self.test_sending_to_stranger()

        # setup for post to work correctly
        self.data = self.data_f_request
        self.url = self.url_dec
        self.headers["HTTP_AUTHORIZATION"] = f"Bearer {generate_token(self.stranger.user_id)}"

        response = self.post()
        response_json = response.json()
        count = FriendRequest.objects.filter(sender=self.user1, receiver=self.stranger, status=FriendRequest.DECLINED).count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count, 1)
        self.assertEqual(response_json["message"], "Friend request declined")
