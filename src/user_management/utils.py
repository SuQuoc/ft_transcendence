from api.models import (
    CustomUser,  # Adjust the import according to your project structure
)
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound


def getUserByDisplayname(displayname):
    try:
        return CustomUser.objects.get(displayname=displayname)
    except CustomUser.DoesNotExist:
        raise NotFound("User doesn't exist")
