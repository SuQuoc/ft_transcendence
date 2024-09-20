from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q

# Create your models here.


class FriendList(models.Model):
    user = models.OneToOneField("api.CustomUser", on_delete=models.CASCADE, related_name="friend_list")
    friends = models.ManyToManyField("api.CustomUser", blank=True, related_name="friends")

    def __str__(self):
        return f"{self.user.displayname}'s friendlist"

    def addFriend(self, user):
        """
        Add new friend
        """
        # if user not in self.friends: # "Adding a second time is OK, it will not duplicate the relation:"
        self.friends.add(user)

    def delFriend(self, user):
        """
        Delete friend
        """
        # if user in self.friends:
        self.friends.remove(user)

    def unfriend(self, to_unfriend):
        initiator_friend_list = self
        try:
            to_unfriend_friend_list = FriendList.objects.get(user=to_unfriend)
        except ObjectDoesNotExist:
            raise ValueError("Smth fundamentally wrong: FriendList - unfriend method")

        initiator_friend_list.del_friend(to_unfriend)
        to_unfriend_friend_list.del_friend(self.user)

    def contains(self, friend):
        if self.friends.filter(user_id=friend.user_id).exists():
            return True
        return False

    def get_friend_count(self):
        return self.friends.count()

    # Needed ??
    def get_friends_with_request_ids(self):
        friends_with_request_id = []
        for friend in self.friends.all():
            friend_request = FriendRequest.objects.filter(
                (Q(sender=self.user) & Q(receiver=friend)) | 
                (Q(sender=friend) & Q(receiver=self.user)),
                status=FriendRequest.ACCEPTED
            ).first()
            friends_with_request_id.append({
                'friend': friend,
                'request_id': friend_request.id if friend_request else None
            })
        return friends_with_request_id

    def get_friends_request_id(self, friend):
        friend_request = self.get_friends_request(friend)
        if friend_request:
            return friend_request.id
        return None

    def get_friends_request(self, friend):
        friend_request = FriendRequest.objects.filter(
            (Q(sender=self.user) & Q(receiver=friend)) | 
            (Q(sender=friend) & Q(receiver=self.user)),
            status=FriendRequest.ACCEPTED
        ).first()
        return friend_request


class FriendRequest(models.Model):
    PENDING = 0
    ACCEPTED = 1
    DECLINED = 2
    UNFRIENDED = 3
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (DECLINED, 'Declined'),
        (UNFRIENDED, 'Unfriended'),
    ]

    sender = models.ForeignKey("api.CustomUser", related_name='sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey("api.CustomUser", related_name='receiver', on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)
    send_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"id: {self.id}, sender: {self.sender} --> receiver: {self.receiver}"

    def accept(self):
        """
        Accept a friend request.
        """
        receiver_friend_list = self.receiver.friend_list
        sender_friend_list = self.sender.friend_list

        receiver_friend_list.addFriend(self.sender)
        sender_friend_list.addFriend(self.receiver)

        self.status = self.ACCEPTED
        self.save()  # This is needed to update the status in the database

    def decline(self):
        """
        Decline a friend request.
        """
        self.status = self.DECLINED
        self.save()

    # Just for fun
    def cancel(self):
        """
        Cancel a friend request that was send.
        """
        if self.status == self.PENDING:
            self.status = self.DECLINED
            self.save()
        else:
            raise ValueError("Cannot cancel a friend request that is not pending.")

    def unfriend(self):
        receiver_friend_list = self.receiver.friend_list
        sender_friend_list = self.sender.friend_list

        receiver_friend_list.delFriend(self.sender)
        sender_friend_list.delFriend(self.receiver)

        self.status = self.UNFRIENDED
        self.save()

    def set_sender_and_receiver(self, *, sender, receiver):
        self.sender = sender
        self.receiver = receiver
        self.status = self.PENDING
        self.save()
