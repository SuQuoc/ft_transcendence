from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import PermissionsMixin
from django.db import models

# Create your models here.


class CustomUser(models.Model):
    # overriding the default user model
    displayname = models.CharField(max_length=20, unique=True, blank=False, null=False)
    # email = models.EmailField(unique=True, blank=False, null=False)
    # password = models.CharField(blank=False, null=False)

    # additional fields
    online = models.BooleanField(default=False)
    friends = models.ManyToManyField("self", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.displayname


class FriendRequest(models.Model):
    STATUS_CHOICES = [(0, 'Pending'), (1, 'Accepted'), (2, 'Declined')]

    from_user = models.ForeignKey(CustomUser, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='to_user', on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)


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
