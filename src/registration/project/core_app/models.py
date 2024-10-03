import uuid, random, string

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class RegistrationUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    username = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128, blank=True)
    backup_code = models.CharField(max_length=128, blank=True)
    email_verified = models.BooleanField(default=False)
    twofa_enabled = models.BooleanField(default=False)
    
    ft_userid = models.PositiveIntegerField(unique=True, null=True)

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
    
    def generate_backup_code(self): # [aguilmea] has to be hashed before saving
        self.backup_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=128))
        self.save()
        return str(self.backup_code)

class OneTimePassword(models.Model):

    ACTION_CHOICES = [
        ('login', 'login'),
        ('signup', 'signup'),
        ('reset_password', 'reset_password'),
        ('change_password', 'change_password'),
        ('change_username', 'change_username'),
        ('delete_user', 'delete_user'),
    ]

    related_user = models.ForeignKey(RegistrationUser, on_delete=models.CASCADE, related_name='OneTimePassword_related_user')
    action = models.CharField(max_length=16, choices=ACTION_CHOICES)
    password = models.CharField(max_length=16)  
    expire = models.DateTimeField(default=timezone.now() + timedelta(minutes=5))

    def delete(self):
        self.expire = timezone.now()
        self.save()
        return self

    def save(self, *args, **kwargs):
        if not self.pk: # if it is a new object, I want to delete all the old ones
            OneTimePassword.objects.filter(related_user=self.related_user).delete()
        super().save(*args, **kwargs) # calls the parent method

    def __str__(self):
        return f"{self.related_user.username} {self.action}"

class OauthTwo(models.Model):

    NEXT_STEP_CHOICES = [
        ('login', 'login'),
        ('signup', 'signup'),
        ('set_oauth2', 'set_oauth2'),
        ('unset_oauth2', 'unset_oauth2'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.CharField(max_length=128)
    next_step = models.CharField(max_length=16, choices=NEXT_STEP_CHOICES)
    related_user = models.ForeignKey(RegistrationUser, on_delete=models.CASCADE, null=True, related_name='OauthTwo_related_user')
    expire = models.DateTimeField(default=timezone.now() + timedelta(minutes=5))

    def delete(self):
        self.expire = timezone.now()
        self.save()
        return self

    def save(self, *args, **kwargs):
        if not self.pk and self.related_user is not None:
            OauthTwo.objects.filter(related_user=self.related_user).delete()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.state} {self.next_step}"
    