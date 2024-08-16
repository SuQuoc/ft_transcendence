
import uuid
import json

from rest_framework.test import APITestCase
from friends.models import FriendRequest
from django.http import QueryDict
from api.models import CustomUser
from django.urls import reverse
from utils_jwt import generate_token

ME = 'MeMario'
I_FRIEND_U = 'i_friend_u'
U_FRIEND_ME = 'u_friend_me'
I_PEND_U = "i_pend_u"
U_PEND_ME = "u_pend_me"
I_DECLINE_U = 'i_decline_u'
U_DECLINE_ME = 'u_decline_me'
STRANGER = 'Stranger'

def create_url_with_query_params(base_url, query_params):
    # Define the query parameters
    query_dict = QueryDict(mutable=True)
    for key, value in query_params.items():
        query_dict[key] = value
    return f"{base_url}?{query_dict.urlencode()}"

def create_user_objs(user_infos):
        users = {}
        for user_data in user_infos:
            user_id = str(uuid.uuid4())
            user_data['user_id'] = user_id  # Add the generated UUID to the user_data dictionary
            user, created = CustomUser.objects.get_or_create(**user_data)
            if created:
                users[user.displayname] = user
        return users

def create_friend_request_objs(user_objs, friend_request_info):
    """
    Creates the request and triggers the models accept and decline to add the person to the FriendList
    """
    requests = []
    for sender, receiver, status in friend_request_info:
        fr = FriendRequest.objects.create(sender=user_objs[sender], receiver=user_objs[receiver], status=status)
        if status == FriendRequest.ACCEPTED:
            fr.accept()
        elif status == FriendRequest.DECLINED:
            fr.decline()
        requests.append(fr)
    return requests

class SearchTest(APITestCase):
    def setUp(self):
        self.test_users = [
            {'displayname': ME, 'online': True},
            {'displayname': I_FRIEND_U, 'online': True},
            {'displayname': U_FRIEND_ME, 'online': True},
            {'displayname': I_PEND_U, 'online': True},
            {'displayname': U_PEND_ME, 'online': True},
            {'displayname': I_DECLINE_U, 'online': True},
            {'displayname': U_DECLINE_ME, 'online': True},
            {'displayname': STRANGER, 'online': True},
            {'displayname': 'Deleted account', 'online': False},
        ]

        # i created a monster
        self.test_friend_requests = [
            # (sender, receiver, status)
            (ME, I_FRIEND_U, FriendRequest.ACCEPTED),
            (U_FRIEND_ME, ME, FriendRequest.ACCEPTED),
            (ME, I_PEND_U, FriendRequest.PENDING),
            (U_PEND_ME, ME, FriendRequest.PENDING),
            (ME, I_DECLINE_U, FriendRequest.PENDING),
            (U_DECLINE_ME, ME, FriendRequest.PENDING),
        ]

        self.user_objs = create_user_objs(self.test_users)
        self.friend_request_objs = create_friend_request_objs(self.user_objs, self.test_friend_requests)

        # generate token and set header
        self.access_token = generate_token(self.user_objs[ME].user_id)
        self.headers = {
            'HTTP_AUTHORIZATION': f'Bearer {self.access_token}',
        }

        self.url = reverse('search')
    

    

    def test_search_friend(self):
        url = create_url_with_query_params(self.url, {"term": "friend"})
        response = self.client.get(url, secure=True, **self.headers)
        response_json = response.json()
        print(json.dumps(response_json, indent=4))
        # self.assertEqual(response.status_code, 210)

    # def test_search_pending(self):
    #     url = create_url_with_query_params(self.url, {"term": "pend"})
    #     response = self.client.get(url, secure=True, **self.headers)
    #     response_json = response.json()
    #     print(json.dumps(response_json, indent=4))
# 
    # def test_search_declined(self):
    #     url = create_url_with_query_params(self.url, {"term": "decline"})
    #     response = self.client.get(url, secure=True, **self.headers)
    #     response_json = response.json()
    #     print(json.dumps(response_json, indent=4))
    # 
    # def test_search_stranger(self):
    #     url = create_url_with_query_params(self.url, {"term": "Stranger"})
    #     response = self.client.get(url, secure=True, **self.headers)
    #     response_json = response.json()
    #     print(json.dumps(response_json, indent=4))
