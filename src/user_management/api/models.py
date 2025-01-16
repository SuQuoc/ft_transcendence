from django.db import models
from friends.models import FriendRequest
from PIL import Image
from django.core.validators import MinLengthValidator
from .validators import displayname_validator

# Create your models here.

UPLOAD_TO_PROFILE = "profile_images/"
DEFAULT_IMAGE_NAME = "default_avatar.png"

# path = MEDIA_ROOT + Name of file
# url  = MEDIA_URL  + Name of file
def print_img(image):
    print(
        f"""===================
image:      {image}
image.path: {image.path}
image.url:  {image.url}
image.name: {image.name}
==================="""
    )


class CustomUser(models.Model):
    user_id = models.UUIDField(primary_key=True, unique=True)
    displayname = models.CharField(max_length=20, unique=True, validators=[MinLengthValidator(1), displayname_validator])  # by default fields are set to be blank=False, null=False
    image = models.ImageField(upload_to=UPLOAD_TO_PROFILE, 
                            default=UPLOAD_TO_PROFILE + DEFAULT_IMAGE_NAME,
                            blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # the instance already exists in the database
        if self.pk:
            # "new image" is default one (user didnt change it)
            if self.image.name.endswith(DEFAULT_IMAGE_NAME):
                super().save(*args, **kwargs)
                return

            # User actually provided a new img or has a non-default
            old_image = CustomUser.objects.get(pk=self.pk).image
            
            super().save(*args, **kwargs) # need to save even if no new img is provided to update other changes
            if old_image != self.image:
                if not old_image.name.endswith(DEFAULT_IMAGE_NAME):
                    old_image.delete(save=False)
    
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
            # with save=True the method would trigger the models save() (with the img)
            # since i do super.save() the imageField = None and then self.image.name will fail
        super().delete(*args, **kwargs)

    # FriendRequests
    def get_pending_received_friend_requests(user):
        return FriendRequest.objects.filter(status=FriendRequest.PENDING, receiver=user)

    def get_pending_requested_friend_requests(user):
        return FriendRequest.objects.filter(status=FriendRequest.PENDING, sender=user)

    def __str__(self):
        return self.displayname

    def get_friend_count(self):
        return self.friend_list.get_friend_count()
