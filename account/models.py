from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.urls import reverse


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


