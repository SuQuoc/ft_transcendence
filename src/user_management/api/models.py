
from django.db import models
from friends.models import FriendRequest
from PIL import Image


# Create your models here.

UPLOAD_TO_PROFILE = "images/profile/"
DEFAULT_IMAGE_NAME = "default/default_avatar.png"


# path = MEDIA_ROOT + Name of file
# url  = MEDIA_URL  + Name of file
def print_img(image):
    print(f"""===================
image:      {image}
image.path: {image.path}
image.url:  {image.url}
image.name: {image.name}
===================""")



class CustomUser(models.Model):
    user_id = models.UUIDField(primary_key=True, unique=True)
    displayname = models.CharField(max_length=20, unique=True)  # by default fields are set to be blank=False, null=False
    online = models.BooleanField(default=False)  # maybe better in registration service, ONLY VISIBLE by FRIENDS
    image = models.ImageField(upload_to=UPLOAD_TO_PROFILE, default=UPLOAD_TO_PROFILE + DEFAULT_IMAGE_NAME, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # the instance already exists in the database
        if self.pk:
            # "new image" is default one (user didnt change it)
            if self.image.name.endswith(DEFAULT_IMAGE_NAME): #(security concerns ??)
                super().save(*args, **kwargs)
                return

            # User actually provided a new img
            old_image = CustomUser.objects.get(pk=self.pk).image
            # print(f"database:")
            # print_img(old_image)
            # print(f"self:")
            # print_img(self.image)

            # old image was custom
            if not old_image.name.endswith(DEFAULT_IMAGE_NAME):
                old_image.delete(save=False)

            # print(f"before super().save:")
            # print_img(self.image)
            super().save(*args, **kwargs)
            # print(f"\nafter super().save:")
            # print_img(self.image)


            img = Image.open(self.image.path)
            if img.height > 220 or img.width > 220:
                output_size = (220, 220)
                img.thumbnail(output_size)
                img.save(self.image.path)
        else:
            super().save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        if not self.image.name.endswith(DEFAULT_IMAGE_NAME):
            self.image.delete(save=False)
            # since the user is deleted anyway i dont save the changes to the database
            # with save=True the method would trigger the models save() (with th img)
            # since i do super.save() the imageField = None and then self.image.name will fail
        super().delete(*args, **kwargs)

    def get_online_status(self):
        return "True" if self.online else "False"

    # FriendRequests
    def get_pending_received_friend_requests(user):
        return FriendRequest.objects.filter(status=FriendRequest.PENDING, receiver=user)

    def get_pending_requested_friend_requests(user):
        return FriendRequest.objects.filter(status=FriendRequest.PENDING, sender=user)

    def __str__(self):
        return self.displayname
