import uuid

from api.models import CustomUser
from django.conf import settings
from django.http import QueryDict
from friends.models import FriendRequest
from rest_framework.test import APITestCase
from utils_jwt import generate_token


class MyTestSetUp(APITestCase):
    @staticmethod
    def create_url_with_query_params(base_url, query_params):
        # Define the query parameters
        query_dict = QueryDict(mutable=True)
        for key, value in query_params.items():
            query_dict[key] = value
        return f"{base_url}?{query_dict.urlencode()}"

    @staticmethod
    def create_user_objs(user_infos):
        users = {}
        for user_data in user_infos:
            user_id = str(uuid.uuid4())
            user_data['user_id'] = user_id  # Add the generated UUID to the user_data dictionary
            user, created = CustomUser.objects.get_or_create(**user_data)
            if created:
                users[user.displayname] = user
        return users

    @staticmethod
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

    def setup_jwt_with_cookie(self, user_id):
        """
        Generates a jwt and puts it in cookie named with SIMPLE_JWT['AUTH_COOKIE'] from django settings
        and SETS the APIClient to use it.
        """
        self.access_token = generate_token(user_id)
        cookie_name = settings.SIMPLE_JWT['AUTH_COOKIE']
        self.client.cookies[cookie_name] = self.access_token
