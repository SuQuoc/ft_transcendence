import uuid

from api.models import (
    CustomUser,  # Adjust the import path according to your project structure
)
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from friends.models import (
    FriendList,  # Adjust the import path according to your project structure
)

TEST_USER1 = 'TestUser1'
TEST_USER2 = 'TestUser2'
TEST_USER3 = 'TestUser3'

class Command(BaseCommand):
    help = 'Creates three test users'

    def handle(self, *args, **kwargs):
        test_users = [
            {'displayname': TEST_USER1, 'online': True},
            {'displayname': TEST_USER2, 'online': True},
            {'displayname': TEST_USER3, 'online': True},
            {'displayname': 'Deleted account', 'online': False},
        ]

        if CustomUser.objects.filter(displayname=TEST_USER1).exists():
            self.stdout.write(f'Test setup already created')
            return

        for user_data in test_users:
            try:
                user_id = str(uuid.uuid4())
                user_data['user_id'] = user_id  # Add the generated UUID to the user_data dictionary
                user, created = CustomUser.objects.get_or_create(**user_data)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully created test user: {user.displayname}'))
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f'Error creating {user_data["displayname"]}: {e}'))
