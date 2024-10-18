import uuid
from encodings.base64_codec import base64_decode, base64_encode

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.utils import timezone
from datetime import timedelta

from .common_utils import generate_random_string
import base64

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

    def save(self, *args, **kwargs):
        self.username = self.username.lower()  # Ensure username is stored in lowercase
        super(RegistrationUser, self).save(*args, **kwargs)

    def set_verified(self):
        self.email_verified = True
        self.save()
        return self

    def is_verified(self):
        return self.email_verified

    def generate_backup_code(self):
        backup_code = generate_random_string(32)
        self.backup_code = make_password(backup_code)
        self.save(update_fields=['backup_code'])
        return backup_code

    def check_backup_code(self, backup_code):
        return check_password(backup_code, self.backup_code)


class OneTimePassword(models.Model):

    ACTION_CHOICES = [
        ('login', 'login'),
        ('signup', 'signup'),
        ('reset_password', 'reset_password'),
        ('change_password', 'change_password'),
        ('change_username_old', 'change_username_old'),
        ('change_username_new', 'change_username_new'),
        ('delete_user', 'delete_user'),
    ]

    related_user = models.ForeignKey(RegistrationUser, on_delete=models.CASCADE, related_name='OneTimePassword_related_user')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    password = models.CharField(max_length=128)
    expire = models.DateTimeField(default=timezone.now() + timedelta(minutes=5))

    def delete(self):
        self.expire = timezone.now()
        self.save()
        return self

    def save(self, *args, **kwargs):
        if not self.pk: # if it is a new object, I want to delete all the old ones
            OneTimePassword.objects.filter(related_user=self.related_user, action=self.action).delete()
        self.password = make_password(self.password)
        super().save(*args, **kwargs) # calls the parent method

    def check_password(self, password):
        return check_password(password, self.password)

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

    def delete(self):
        self.expire = timezone.now()
        self.save()
        return self

    def save(self, *args, **kwargs):
        if not self.pk and self.related_user is not None: # [aguilmea] when do i delete the oauth2 without related_user?
            OauthTwo.objects.filter(related_user=self.related_user).delete()
        self.state = base64.b64encode(self.state.encode('utf-8')).decode('utf-8')
        #self.state = make_password(self.state)
        super().save(*args, **kwargs)

    def check_state(self, state):
        #return check_password(state, self.state)
        decoded_state = base64.b64decode(self.state.encode('utf-8')).decode('utf-8')
        return decoded_state == state

    def get_hashed_state(self):
        return self.state

    def __str__(self):
        return f"{self.state} {self.next_step}"
