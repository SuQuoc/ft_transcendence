import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    username = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128, null=True)
    
    enabledtwofa = models.BooleanField(default=False)
    
    ft_userid = models.PositiveIntegerField(unique=True, null=True) #[aguilmea] I added this field to store the 42 intra userid, not sure if it is okay without encrypting it but i guess since it is not a credential

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'username'


    def __str__(self):
        return self.username