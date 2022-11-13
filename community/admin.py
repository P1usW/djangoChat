from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Group, Post


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin', 'subscribers_count', 'posts_count', 'group_img')
    search_fields = ('name',)

    @admin.display(description='Фотография группы')
    def group_img(self, obj):
        if obj.group_image:
            return mark_safe(f'<img src="{obj.group_image.url}" width="70"')
        else:
            return '-'

    @admin.display(description='Количество подписчиков')
    def subscribers_count(self, obj):
        return obj.subscribers.count()

    @admin.display(description='Количество записей')
    def posts_count(self, obj):
        return obj.posts.count()


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('group_author', 'user_author', 'timestamp')
    search_fields = ('content',)
    readonly_fields = ('timestamp',)

    @admin.display(description='User Author')
    def user_author(self, obj):
        if obj.user_author:
            return obj.user_author
        return '-'
