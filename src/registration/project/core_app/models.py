import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(max_length=150, unique=True, verbose_name='username')
    password = models.CharField(max_length=128, verbose_name='password')
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='last login')
    first_name = models.CharField(blank=True, max_length=150, verbose_name='first name')
    last_name = models.CharField(blank=True, max_length=150, verbose_name='last name')
    email = models.EmailField(max_length=254, unique=True, verbose_name='email address')
    enabled2fa = models.BooleanField(default=False, verbose_name='2FA enabled')
    
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']
    USERNAME_FIELD = 'username'
