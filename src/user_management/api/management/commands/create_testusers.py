import uuid

from api.models import (
    CustomUser,  # Adjust the import path according to your project structure
)
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from friends.models import FriendRequest

ME = 'MeMario'
I_FRIEND_U = 'i_friend_u'
U_FRIEND_ME = 'u_friend_me'
I_PEND_U = "i_pend_u"
U_PEND_ME = "u_pend_me"
I_DECLINE_U = 'i_decline_u'
U_DECLINE_ME = 'u_decline_me'
STRANGER = 'Stranger'


class Command(BaseCommand):
    help = 'Creates three test users'

    def handle(self, *args, **kwargs):
        self.test_users = [
            {'displayname': ME}, #, 'online': True},
            {'displayname': I_FRIEND_U}, #, 'online': True},
            {'displayname': U_FRIEND_ME}, #, 'online': True},
            {'displayname': I_PEND_U}, #, 'online': True},
            {'displayname': U_PEND_ME}, #, 'online': True},
            {'displayname': I_DECLINE_U}, #, 'online': True},
            {'displayname': U_DECLINE_ME}, #, 'online': True},
            {'displayname': STRANGER}, #, 'online': True},
            {'displayname': 'Deleted account'}, #, 'online': False},
        ]

        # i created a monster
        self.relationships = [
            # (sender, receiver, status)
            (ME, I_FRIEND_U, FriendRequest.ACCEPTED),
            (U_FRIEND_ME, ME, FriendRequest.ACCEPTED),
            (ME, I_PEND_U, FriendRequest.PENDING),
            (U_PEND_ME, ME, FriendRequest.PENDING),
            (ME, I_DECLINE_U, FriendRequest.PENDING),
            (U_DECLINE_ME, ME, FriendRequest.PENDING),
        ]

        if CustomUser.objects.filter(displayname=ME).exists():
            self.stdout.write('Test setup already created')
            return

        self.create_users()
        self.send_friend_request()

    def create_users(self):
        self.users = {}
        for user_data in self.test_users:
            try:
                user_id = str(uuid.uuid4())
                user_data['user_id'] = user_id  # Add the generated UUID to the user_data dictionary
                user, created = CustomUser.objects.get_or_create(**user_data)
                if created:
                    self.users[user.displayname] = user
                    self.stdout.write(self.style.SUCCESS(f'Successfully created test user: {user.displayname}'))
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f'Error creating {user_data["displayname"]}: {e}'))

    def send_friend_request(self):
        self.requests = []

        for sender, receiver, status in self.relationships:
            fr = FriendRequest.objects.create(sender=self.users[sender], receiver=self.users[receiver], status=status)
            self.requests.append(fr)
