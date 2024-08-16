
from django.dispatch import receiver
from django.db.models.signals import post_save
from api.models import CustomUser
from . models import FriendList

@receiver(post_save, sender=CustomUser)
def receiver(sender, instance, created, **kwargs):
    if created:
        FriendList.objects.create(user=instance)
