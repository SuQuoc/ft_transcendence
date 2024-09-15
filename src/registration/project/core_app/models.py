import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class RegistrationUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    username = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128, blank=True)
    
    email_verified = models.BooleanField(default=False)
    twofa_enabled = models.BooleanField(default=False)
    
    ft_userid = models.PositiveIntegerField(unique=True, null=True) #[aguilmea] I added this field to store the 42 intra userid, not sure if it is okay without encrypting it but i guess since it is not a credential

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username
    
    def set_verified(self):
        self.email_verified = True
        self.save()
        return self

    def is_verified(self):
        return self.email_verified

class OneTimePassword(models.Model):

    ACTION_CHOICES = [
        ('login', 'login'),
        ('signup', 'signup'),
        ('reset_password', 'reset_password'),
        ('change_password', 'change_password'),
        ('change_email', 'change_email'),
        ('delete_user', 'delete_user'),
    ]

    related_user = models.ForeignKey(RegistrationUser, on_delete=models.CASCADE, related_name='otp')
    action = models.CharField(max_length=16, choices=ACTION_CHOICES)
    password = models.CharField(max_length=16)  
    expire = models.DateTimeField(default=timezone.now() + timedelta(minutes=5))

    def delete(self):
        self.expire = timezone.now()
        self.save()
        return self

    def __str__(self):
        return f"{self.related_user.username} {self.action}"
