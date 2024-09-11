import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    username = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128, blank=True)
    
    twofa_enabled = models.BooleanField(default=False)
    
    ft_userid = models.PositiveIntegerField(unique=True, null=True) #[aguilmea] I added this field to store the 42 intra userid, not sure if it is okay without encrypting it but i guess since it is not a credential

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

class OneTimePassword(models.Model):

    ACTION_CHOICES = [
        ('twofa_enable', 'enable the two factor authentication'),
        ('twofa_disable', 'disable the two factor authentication'),
        ('twofa_login', 'login'),
        ('reset_password', 'reset the login password'),
    ]

    related_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otp')
    action = models.CharField(max_length=16, choices=ACTION_CHOICES)
    password = models.CharField(max_length=16)  
    expire = models.DateTimeField(default=timezone.now() + timedelta(minutes=5))

    def __str__(self):
        return f"{self.related_user.username} {self.action}"
