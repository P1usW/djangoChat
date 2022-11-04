from django.db import models
from django.conf import settings


def file_up_load(instance, filename):
    return 'profile/user_{0}/{1}'.format(instance.username, filename)


def get_default_profile_image():
    return 'default_images/non_images-group.jpg'


class Group(models.Model):
    name = models.CharField(max_length=128)
    information = models.CharField(max_length=4098)
    group_image = models.ImageField(verbose_name='Фотография', null=True, blank=True,
                                    upload_to=file_up_load, default=get_default_profile_image)
    subscribers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)


class Post(models.Model):
    content = models.CharField(max_length=4098)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                    related_name='user_author', blank=True, null=True)
    group_author = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_author')
    group = models.ManyToManyField(Group, related_name='group')
