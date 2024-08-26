import uuid

from api.models import CustomUser
from django.db import connection
from django.urls import reverse
from friends.models import FriendRequest
from test_setup import MyTestSetUp
from utils_jwt import generate_token


class FriendRequestTest(MyTestSetUp):
    def setUp(self):
        self.user1 = CustomUser.objects.create(user_id=uuid.uuid4(), displayname="TestUser1", online=False)
        self.stranger = CustomUser.objects.create(user_id=uuid.uuid4(), displayname="Stranger", online=True)

        self.user_tokens = {  # old JWT WITHOUT COOKIE:
            f"{self.user1.displayname}": f"{generate_token(self.user1.user_id)}",
            f"{self.stranger.displayname}": f"{generate_token(self.stranger.user_id)}",
        }

        self.data = {"receiver": "SET THIS IN EACH TEST FUNCTION"}

        self.data_f_request = {"friend_request_id": "1"}

        self.url = reverse("send-friend-request")
        self.url_send = reverse("send-friend-request")
        self.url_acc = reverse("acc-friend-request")
        self.url_dec = reverse("dec-friend-request")

        self.setup_jwt_with_cookie(self.user1.user_id)

        self.headers = {
            # "HTTP_AUTHORIZATION": f"Bearer {self.user_tokens[self.user1.displayname]}",
        }

        # to reset the id to start with 1 for every test method,
        # if not done the id's will auto increment even though theres no other friendRequest in table
        # TLDR: without it i had one friend request in table with id of 2
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE friends_friendrequest RESTART IDENTITY CASCADE;")

    def tearDown(self):
        # Clean up after each test
        FriendRequest.objects.all().delete()
        CustomUser.objects.all().delete()

    # old
    def set_request_user(self, displayname):
        self.headers["HTTP_AUTHORIZATION"] = f"Bearer {self.user_tokens[displayname]}"

    def post(self):
        return self.client.post(self.url, data=self.data, format="json", secure=True, **self.headers)

    def test_sending_to_myself(self):
        self.data["receiver"] = self.user1.displayname
        response = self.post()
        response_json = response.json()

        # print(response)
        # print(response_json)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json["error"], "You can't send a friend request to yourself")

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

    def test_sending_to_friend(self):
        self.test_accept_friend_request()

        self.url = self.url_send
        self.data["receiver"] = self.stranger.displayname  # stranger became a friend via code before

        self.setup_jwt_with_cookie(self.user1.user_id)

        response = self.post()
        response_json = response.json()
        count = FriendRequest.objects.filter(sender=self.user1, receiver=self.stranger, status=FriendRequest.ACCEPTED).count()

        self.assertEqual(count, 1)
        self.assertEqual(response_json["error"], "You are best buds")
        self.assertEqual(response.status_code, 400)

    # Answering a friend request
    def test_accept_friend_request(self):
        """
        after this test APIClient uses cookie created with stranger
        """
        self.test_sending_to_stranger()

        # setup for post to work correctly
        self.data = self.data_f_request
        self.url = self.url_acc
        self.setup_jwt_with_cookie(self.stranger.user_id)

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
        # JWT WITHOUT COOKIE: self.headers["HTTP_AUTHORIZATION"] = f"Bearer {generate_token(self.stranger.user_id)}"
        self.setup_jwt_with_cookie(self.stranger.user_id)
        response = self.post()
        response_json = response.json()
        count = FriendRequest.objects.filter(sender=self.user1, receiver=self.stranger, status=FriendRequest.DECLINED).count()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(count, 1)
        self.assertEqual(response_json["message"], "Friend request declined")
