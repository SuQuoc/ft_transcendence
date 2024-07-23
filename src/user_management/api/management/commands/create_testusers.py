import uuid

from api.models import (
    CustomUser,  # Adjust the import path according to your project structure
)
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = 'Creates three test users'

    def handle(self, *args, **kwargs):
        test_users = [
            {'displayname': 'TestUser1', 'online': False},
            {'displayname': 'TestUser2', 'online': False},
            {'displayname': 'Deleted account', 'online': False},
        ]

        for user_data in test_users:
            if CustomUser.objects.filter(displayname=user_data['displayname']).exists():
                self.stdout.write(f'Test user {user_data["displayname"]} already exists.')
                continue  # Skip to the next user_data if this user already exists
            try:
                user_id = str(uuid.uuid4())
                user_data['user_id'] = user_id  # Add the generated UUID to the user_data dictionary
                user, created = CustomUser.objects.get_or_create(**user_data)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully created test user: {user.displayname}'))
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f'Error creating {user_data["displayname"]}: {e}'))
