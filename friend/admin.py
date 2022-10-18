from django.contrib import admin
from .models import FriendList, FriendRequest


@admin.register(FriendList)
class FriendListAdmin(admin.ModelAdmin):
    list_display = ('user', 'count_friends')
    search_fields = ('user',)

    @admin.display(description='Количество друзей')
    def count_friends(self, obj):
        return obj.friends.count()


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver',)
    list_filter = ('sender', 'receiver',)
    search_fields = ('sender__username', 'receiver__username',)