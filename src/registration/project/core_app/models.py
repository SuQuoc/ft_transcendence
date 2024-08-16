import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)
    enabled2fa = models.BooleanField(default=False)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'username'
