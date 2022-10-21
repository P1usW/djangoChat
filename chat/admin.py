from django.contrib import admin

from chat.models import PrivateChatRoom, PrivateRoomChatMessage


@admin.register(PrivateChatRoom)
class PrivateChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'user1', 'user2', 'is_active']
    search_fields = ['id', 'user1__username', 'user2__username', 'user1__email', 'user2__email', ]
    readonly_fields = ['id', ]
    list_editable = ['is_active',]
    list_display_links = ['id', 'user1', 'user2',]

    class Meta:
        model = PrivateChatRoom


@admin.register(PrivateRoomChatMessage)
class RoomChatMessageAdmin(admin.ModelAdmin):
    list_filter = ['room', 'user', "timestamp"]
    list_display = ['room', 'user', 'content', "timestamp"]
    search_fields = ['user__username', 'content']
    readonly_fields = ['id', "user", "room", "timestamp"]

    show_full_result_count = False

    class Meta:
        model = PrivateRoomChatMessage
