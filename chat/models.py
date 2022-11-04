from django.db import models
from django.db.models.signals import pre_save, post_save
from django.conf import settings


class PrivateChatRoom(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user2')
    connected_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="connected_users")
    is_active = models.BooleanField(default=False)

    def connect_user(self, user):
        is_user_added = False
        if not user in self.connected_users.all():
            self.connected_users.add(user)
            is_user_added = True
        return is_user_added

    def disconnect_user(self, user):
        is_user_removed = False
        if user in self.connected_users.all():
            self.connected_users.remove(user)
            is_user_removed = True
        return is_user_removed

    @property
    def group_name(self):
        return f"PrivateChatRoom-{self.id}"

    def __str__(self):
        return f"PrivateChatRoom-{self.id}"


class RoomChatMessageManager(models.Manager):
    def by_room(self, room):
        qs = PrivateRoomChatMessage.objects.filter(room=room).order_by("timestamp")
        return qs


class PrivateRoomChatMessage(models.Model):
    """
    Chat message created by a user inside a Room
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(PrivateChatRoom, on_delete=models.CASCADE, related_name='private_messages')
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField(unique=False, blank=False,)

    objects = RoomChatMessageManager()

    def __str__(self):
        return self.content

    @property
    def get_other_user(self):
        """
        Get the other user in the chat room
        """
        if self.user == self.room.user1:
            return self.room.user2
        else:
            return self.room.user1