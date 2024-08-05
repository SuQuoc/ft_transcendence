from api.models import (
    CustomUser,  # Adjust the import according to your project structure
)
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound


def getUser(lookup_field, lookup_value):
    try:
        return CustomUser.objects.get(**{lookup_field: lookup_value})
    except CustomUser.DoesNotExist:
        raise NotFound("User doesn't exist")
