import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import PermissionsMixin
from django.db import models

# Create your models here.


class CustomUser(models.Model):
    user_id = models.UUIDField(primary_key=True, unique=True)
    displayname = models.CharField(max_length=20, unique=True)  # by default fields are set to be blank=False, null=False
    online = models.BooleanField(default=False)  # maybe better in registration service, ONLY VISIBLE by FRIENDS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.displayname


# all the records associated with the user: user.matchrecord_set.all()
# with the related name i can easier filter for all the records where this user has won: user.wins.all()
# class MatchRecord(models.Model):
#     winner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="wins")
#     loser = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="losses")
#     winner_score = models.IntegerField()
#     loser_score = models.IntegerField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return f"Score: {self.winner_score} - {self.loser_score}\nWinner: {self.winner.username}\nLoser: {self.loser.username}"
