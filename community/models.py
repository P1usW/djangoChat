from django.db import models
from django.conf import settings
from django.core.validators import validate_slug
from django.urls import reverse


def file_up_load(instance, filename):
    string = instance.name.split()
    name = ''.join(string)
    return 'group/group_id-{0}_{1}/{2}'.format(instance.pk, name, filename)


def get_default_profile_image():
    return 'default_images/non_images-group.jpg'


class Group(models.Model):
    name = models.CharField(max_length=128, db_index=True, verbose_name='Имя группы')
    uniq_name_url = models.CharField(max_length=32, unique=True, verbose_name='Уникальное имя в ссылке',
                                     validators=[validate_slug])
    information = models.TextField(max_length=4098, blank=True, verbose_name='Информация')
    group_image = models.ImageField(verbose_name='Фотография', null=True, blank=True,
                                    upload_to=file_up_load, default=get_default_profile_image)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT,
                              related_name='group_admin', verbose_name='Администратор группы')
    moderators = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='group_moderator',
                                        verbose_name='Модераторы')
    subscribers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='group_sub',
                                         verbose_name='Подписчики')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('group', kwargs={'uniq_name': self.uniq_name_url})


class Post(models.Model):
    content = models.TextField(max_length=4098)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    related_name='user_post_author', blank=True, null=True)
    group_author = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_post_author')
    group = models.ManyToManyField(Group, related_name='posts')
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='post_likes')
