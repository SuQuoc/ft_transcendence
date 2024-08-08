import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from PIL import Image
from django.conf import settings
import os
from django.templatetags.static import static


# Create your models here.

DEFAULT_IMAGE_NAME = "default/default_avatar.png"

class CustomUser(models.Model):
    user_id = models.UUIDField(primary_key=True, unique=True)
    displayname = models.CharField(max_length=20, unique=True)  # by default fields are set to be blank=False, null=False
    online = models.BooleanField(default=False)  # maybe better in registration service, ONLY VISIBLE by FRIENDS
    image = models.ImageField(upload_to="images/profile/", default="images/profile/" + DEFAULT_IMAGE_NAME, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    # @property
    # def image_url(self):
    #     ""
    #     if self.image:
    #         return self.image.url
    #     else:
    #         return static(DEFAULT_IMAGE_NAME)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Check if the image is the default one
        if self.image.name.endswith(DEFAULT_IMAGE_NAME):
            return

        print(f"""===================
                    image.path: {self.image.path}
                    image.url: {self.image.url}
                    image.name: {self.image.name}
                    ===================""")

        img = Image.open(self.image.path)
        # Resize the image
        if img.height > 220 or img.width > 220:
            output_size = (220, 220)
            img.thumbnail(output_size)
            img.save(self.image.path)


    def delete(self, *args, **kwargs):
        self.image.delete(save=True)
        super().delete(*args, **kwargs)

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
