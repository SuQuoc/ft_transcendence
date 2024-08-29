import uuid

from api.models import CustomUser
from django.db import connection
from django.urls import reverse
from friends.models import FriendRequest
from friends.serializers import FriendRequestAnswerSerializer
from test_setup import MyTestSetUp
from utils_jwt import generate_token

ANS = FriendRequestAnswerSerializer


class FriendRequestTest(MyTestSetUp):
    def setUp(self):
        self.user1 = CustomUser.objects.create(user_id=uuid.uuid4(), displayname="TestUser1", online=False)
        self.stranger = CustomUser.objects.create(user_id=uuid.uuid4(), displayname="Stranger", online=True)

        self.user_tokens = {  # old JWT WITHOUT COOKIE:
            f"{self.user1.displayname}": f"{generate_token(self.user1.user_id)}",
            f"{self.stranger.displayname}": f"{generate_token(self.stranger.user_id)}",
        }

        self.data_send = {"receiver": "SET THIS"}

        self.data_answer = {
            "friend_request_id": "1",
            "action": "SET THIS",
        }

        self.url = reverse("send-friend-request")
        self.url_send = reverse("send-friend-request")
        self.url_answer = reverse("answer-friend-request")

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

    # TESTS
    def test_sending_to_myself(self):
        response = self.send_friend_request(sender=self.user1, receiver=self.user1)
        response_json = response.json()

        # print(response)
        # print(response_json)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json["error"], "You can't send a friend request to yourself")

    def test_sending_to_stranger(self):
        response = self.send_friend_request(sender=self.user1, receiver=self.stranger)
        response_json = response.json()

        count = FriendRequest.objects.filter(sender=self.user1, receiver=self.stranger, status=FriendRequest.PENDING).count()
        self.assertEqual(count, 1)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json["message"], "friend request sent")

    def test_sending_to_stranger_twice(self):
        response = self.send_friend_request(sender=self.user1, receiver=self.stranger)
        response = self.send_friend_request(sender=self.user1, receiver=self.stranger)
        response_json = response.json()

        count = FriendRequest.objects.filter(sender=self.user1, receiver=self.stranger, status=FriendRequest.PENDING).count()
        self.assertEqual(count, 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["message"], "friend request already sent, be patient")

    def test_sending_to_friend(self):
        self.test_accept_friend_request()

        response = self.send_friend_request(sender=self.user1, receiver=self.stranger)
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
        response = self.answer_on_friend_request(user=self.stranger, answer=ANS.ACCEPT)
        response_json = response.json()

        count = FriendRequest.objects.filter(sender=self.user1, receiver=self.stranger, status=FriendRequest.ACCEPTED).count()
        self.assertEqual(count, 1)
        self.assertEqual(self.user1.get_friend_count(), 1)
        self.assertEqual(self.stranger.get_friend_count(), 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["message"], "Friend request accepted")

    def test_decline_friend_request(self):
        self.test_sending_to_stranger()

        response = self.answer_on_friend_request(user=self.stranger, answer=ANS.DECLINE)
        response_json = response.json()

        count = FriendRequest.objects.filter(sender=self.user1, receiver=self.stranger, status=FriendRequest.DECLINED).count()
        self.assertEqual(count, 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["message"], "Friend request declined")

    # Actions after an ACCEPTED FR
    def test_decline_friend_request_after_accepting(self):
        self.test_sending_to_stranger()
        self.answer_on_friend_request(user=self.stranger, answer=ANS.ACCEPT)
        response = self.answer_on_friend_request(user=self.stranger, answer=ANS.DECLINE)

        self.assertEqual(response.json()["error"], "Action not allowed on ACCEPTED friend request")

    def test_accepting_friend_request_twice(self):
        self.test_sending_to_stranger()
        self.answer_on_friend_request(user=self.stranger, answer=ANS.ACCEPT)
        response = self.answer_on_friend_request(user=self.stranger, answer=ANS.ACCEPT)

        self.assertEqual(response.json()["error"], "Action not allowed on ACCEPTED friend request")

    def test_sender_unfriends(self):
        self.test_sending_to_stranger()
        self.answer_on_friend_request(user=self.stranger, answer=ANS.ACCEPT)
        response = self.answer_on_friend_request(user=self.user1, answer=ANS.UNFRIEND)

        count = FriendRequest.objects.filter(sender=self.user1, receiver=self.stranger, status=FriendRequest.UNFRIENDED).count()
        self.assertEqual(count, 1)
        self.assertEqual(self.user1.get_friend_count(), 0)
        self.assertEqual(self.stranger.get_friend_count(), 0)
        self.assertEqual(response.json()["message"], "Unfriended user")

    def test_receiver_unfriends(self):
        self.test_sending_to_stranger()
        self.answer_on_friend_request(user=self.stranger, answer=ANS.ACCEPT)
        response = self.answer_on_friend_request(user=self.stranger, answer=ANS.UNFRIEND)

        count = FriendRequest.objects.filter(sender=self.user1, receiver=self.stranger, status=FriendRequest.UNFRIENDED).count()
        self.assertEqual(count, 1)
        self.assertEqual(self.user1.get_friend_count(), 0)
        self.assertEqual(self.stranger.get_friend_count(), 0)
        self.assertEqual(response.json()["message"], "Unfriended user")

    def test_reverse_friend_request(self):
        self.test_sending_to_stranger()
        response = self.send_friend_request(sender=self.stranger, receiver=self.user1)

        self.assertEqual(response.json()["message"], "The other person send u a request already, check inbox")

    def test_reverse_friend_request_after_unfriending(self):
        self.test_sender_unfriends()
        response = self.send_friend_request(sender=self.stranger, receiver=self.user1)

        count0 = FriendRequest.objects.filter(sender=self.user1, receiver=self.stranger, status=FriendRequest.PENDING).count()
        count1 = FriendRequest.objects.filter(sender=self.stranger, receiver=self.user1, status=FriendRequest.PENDING).count()
        self.assertEqual(count0, 0)
        self.assertEqual(count1, 1)
        self.assertEqual(response.json()["message"], "friend request sent")

    def test_accept_reverse_friend_request_after_unfriending(self):
        self.test_reverse_friend_request_after_unfriending()
        response = self.answer_on_friend_request(user=self.user1, answer=ANS.ACCEPT)

        count0 = FriendRequest.objects.filter(sender=self.user1, receiver=self.stranger, status=FriendRequest.ACCEPTED).count()
        count1 = FriendRequest.objects.filter(sender=self.stranger, receiver=self.user1, status=FriendRequest.ACCEPTED).count()
        self.assertEqual(count0, 0)
        self.assertEqual(count1, 1)
        self.assertEqual(self.user1.get_friend_count(), 1)
        self.assertEqual(self.stranger.get_friend_count(), 1)

    # UTILS
    def send_friend_request(self, *, sender: CustomUser, receiver: CustomUser):
        self.set_sender_and_receiver(sender=sender, receiver=receiver)
        response = self.client.post(self.url, data=self.data_send, format="json", secure=True, **self.headers)
        return response

    def answer_on_friend_request(self, *, user: CustomUser, answer: str):
        self.set_users_answer(user=user, answer=answer)
        response = self.client.post(self.url_answer, data=self.data_answer, format="json", secure=True, **self.headers)
        return response

    def post(self):
        return self.client.post(self.url, data=self.data_send, format="json", secure=True, **self.headers)

    def set_sender_and_receiver(self, *, sender, receiver):
        self.setup_jwt_with_cookie(sender.user_id)
        self.data_send["receiver"] = receiver.displayname

    def set_users_answer(self, *, user, answer):
        self.setup_jwt_with_cookie(user.user_id)
        self.data_answer["action"] = answer

    # old
    def set_request_user(self, displayname):
        self.headers["HTTP_AUTHORIZATION"] = f"Bearer {self.user_tokens[displayname]}"
