from api.models import CustomUser
from django.db import models

# Create your models here.


class FriendList(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="friend_list")
    friends = models.ManyToManyField(CustomUser, blank=True, related_name="friends")

    def __str__(self):
        return self.user.displayname

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
        to_unfriend_friend_list = FriendList.objects.get(user=to_unfriend)

        initiator_friend_list.del_friend(to_unfriend)
        to_unfriend_friend_list.del_friend(self.user)

    def isFriend(self, friend):
        if friend in self.friends:
            return True
        return False


class FriendRequest(models.Model):
    PENDING = 0
    ACCEPTED = 1
    DECLINED = 2
    UNFRIENDED = 3
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (DECLINED, 'Declined'),
    ]

    sender = models.ForeignKey(CustomUser, related_name='sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name='receiver', on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)
    send_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"sender: {self.sender}, receiver: {self.receiver}"

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

    # def accept(self):
    #     receiver_friend_list = FriendList.objects.get(user=self.receiver)
    #     if receiver_friend_list:
    #         receiver_friend_list.add_friend(self.sender)
    #         sender_friend_list = FriendList.objects.get(user=self.sender)
    #         if sender_friend_list:
    #             receiver_friend_list.add_friend(self.sender)
    #             self.status = self.ACCEPTED
    #             self.save()

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
            self.delete()
        else:
            raise ValueError("Cannot cancel a friend request that is not pending.")
