from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.urls import reverse
from django.conf import settings

from django.db.models.signals import post_save
from django.dispatch import receiver


class AccountManager(UserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        username = username.lower()
        if not email:
            raise ValueError('Пользователь должен иметь почту')
        if not extra_fields.get('first_name'):
            raise ValueError('Пользователь должен иметь Имя')
        if not extra_fields.get('last_name'):
            raise ValueError('Пользователь должен иметь Фамилию')
        return super().create_user(username, email=None, password=None, **extra_fields)


def file_up_load(instance, filename):
    return 'profile/user_{0}/{1}'.format(instance.username, filename)


def get_default_profile_image():
    return 'default_images/non_images.jpg'


class Account(AbstractUser):
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    date_joined = models.DateTimeField(verbose_name='Дата вступления', auto_now_add=True)
    profile_image = models.ImageField(verbose_name='Фотография', upload_to=file_up_load, null=True, blank=True,
                                      default=get_default_profile_image)
    about_me = models.TextField(max_length=4096, null=True, blank=True)
    facebook = models.CharField(max_length=64, null=True, blank=True)
    twitter = models.CharField(max_length=64, null=True, blank=True)
    instagram = models.CharField(max_length=64, null=True, blank=True)

    objects = AccountManager()

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.username})

    class Meta:
        swappable = "AUTH_USER_MODEL"


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
        print(self)
        print(account)
        if not account in self.friends.all() and self == account:
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
