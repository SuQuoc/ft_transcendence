import json

from django.urls import reverse
from friends.models import FriendRequest
from rest_framework.test import APITestCase
from test_setup import MyTestSetUp

ME = 'MeMario'
I_FRIEND_U = 'i_friend_u'
U_FRIEND_ME = 'u_friend_me'
I_PEND_U = "i_pend_u"
U_PEND_ME = "u_pend_me"
I_DECLINE_U = 'i_decline_u'
U_DECLINE_ME = 'u_decline_me'
STRANGER = 'Stranger'


class ViewingFriendPageTest(MyTestSetUp):
    def setUp(self):
        self.test_users = [
            {'displayname': ME},
            {'displayname': I_FRIEND_U},
            {'displayname': U_FRIEND_ME},
            {'displayname': I_PEND_U},
            {'displayname': U_PEND_ME},
            {'displayname': I_DECLINE_U},
            {'displayname': U_DECLINE_ME},
            {'displayname': STRANGER},
            {'displayname': 'Deleted account'},
        ]

        # i created a monster
        self.test_friend_requests = [
            # (sender, receiver, status)
            (ME, I_FRIEND_U, FriendRequest.ACCEPTED),
            (U_FRIEND_ME, ME, FriendRequest.ACCEPTED),
            (ME, I_PEND_U, FriendRequest.PENDING),
            (U_PEND_ME, ME, FriendRequest.PENDING),
            (ME, I_DECLINE_U, FriendRequest.DECLINED),
            (U_DECLINE_ME, ME, FriendRequest.DECLINED),
        ]

        self.user_objs = self.create_user_objs(self.test_users)
        self.friend_request_objs = self.create_friend_request_objs(self.user_objs, self.test_friend_requests)

        self.setup_jwt_with_cookie(self.user_objs[ME].user_id)
        self.headers = {
            # 'HTTP_AUTHORIZATION': f'Bearer {self.access_token}',
        }

        self.url = reverse("friends")

    def test_friends(self):
        response = self.client.get(self.url, secure=True, **self.headers)
        response_json = response.json()

        print(json.dumps(response_json, indent=4))
        
        expected = [
            {
                "displayname": I_FRIEND_U,
                "relationship": "friend",
            },
            {
                "displayname": U_FRIEND_ME,
                "relationship": "friend",
            },
            {
                "displayname": I_PEND_U,  # This person doesnt answer your request
                "relationship": "requested",
            },
            {
                "displayname": U_PEND_ME,
                "relationship": "received",
            },
        ]

        # print(json.dumps(response_json, indent=4))

        for expected_user in expected:
            self.assertTrue(contains_expected_user(response_json, expected_user))


def contains_expected_user(response_json, expected_user):
    # print(f"Checking for expected user: {expected_user}")
    for item in response_json:
        # print(f"Checking item: {item}")
        if all(item.get(key) == value for key, value in expected_user.items()):
            # print("Match found!")
            return True
    # print("No match found.")
    return False
