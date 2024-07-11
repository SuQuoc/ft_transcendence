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
            try:
                user, created = CustomUser.objects.get_or_create(**user_data)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully created test user: {user.displayname}'))
                else:
                    self.stdout.write(f'Test user {user.displayname} already exists.')
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f'Error creating {user_data["displayname"]}: {e}'))
