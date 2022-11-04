from django.db import models
from django.conf import settings
from account.models import Account

from django.db.models.signals import post_save
from django.dispatch import receiver


class FriendList(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user')
    friends = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='friends')

    def __str__(self):
        return self.user.username

    def add_friend(self, account):
        """
        Add friend
        :param account:
        :return:
        """
        if not account in self.friends.all() and self != account:
            self.friends.add(account)
            self.save()

    def remove_friend(self, account):
        """
        Remove friend
        :param account:
        :return:
        """
        if account in self.friends.all():
            self.friends.remove(account)
            self.save()

    def is_mutual_fiend(self, friend):
        """
        Они друзья?
        :param friend:
        :return True or False:
        """
        if friend in self.friends.all():
            return True
        return False


@receiver(post_save, sender=Account)
def user_save(sender, instance, **kwargs):
    FriendList.objects.get_or_create(user=instance)


class FriendRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='receiver')
    is_active = models.BooleanField(blank=False, null=False, default=True)

    def __str__(self):
        return self.sender.username

    def accept(self):
        """
        Accept friend
        """
        receiver_friend_list = FriendList.objects.get(user=self.receiver)
        if receiver_friend_list:
            receiver_friend_list.add_friend(self.sender)
            sender_friend_list = FriendList.objects.get(user=self.sender)
            if sender_friend_list:
                sender_friend_list.add_friend(self.receiver)
                self.is_active = False
                self.save()

    def decline(self):
        self.is_active = False
        self.save()

    def cancel(self):
        self.is_active = False
        self.save()
