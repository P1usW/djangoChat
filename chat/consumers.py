import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from account.models import Account

from friend.models import FriendList
from .models import PrivateChatRoom, PrivateRoomChatMessage
from .exceptions import ClientError


class AsyncChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            })

    # Receive message from room group
    async def chat_message(self, event):
        username = self.scope['user'].username
        message = username + ': ' + event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


class PrivateAsyncChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        pass

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def chat_message(self, event):
        pass


@database_sync_to_async
def create_room_chat_messages(room, user, messages):
    return PrivateRoomChatMessage.objects.create(user=user, room=room, content=messages)


@database_sync_to_async
def get_room_chat_messages(room, page_number=None):
    try:
        qs = PrivateRoomChatMessage.objects.by_room(room)
        payload = {'messages': qs}
        return json.dumps(payload)
    except Exception as e:
        print('EXCEPTION: ' + str(e))
    return None


@database_sync_to_async
def get_room_or_error(room_id, user):
    """
    Tries to fetch a room for the user, checking permissions along the way.
    """
    try:
        room = PrivateChatRoom.objects.get(pk=room_id)
    except PrivateChatRoom.DoesNotExist:
        raise ClientError("ROOM_INVALID", "Комната не найдена.")

    # Is this user allowed in the room? (must be user1 or user2)
    if user != room.user1 and user != room.user2:
        raise ClientError("ROOM_ACCESS_DENIED", "У вас нет прав на вступление в данную комнату.")

    # Are the users in this room friends?
    friend_list = FriendList.objects.get(user=user).friends.all()
    if not room.user1 in friend_list:
        if not room.user2 in friend_list:
            raise ClientError("ROOM_ACCESS_DENIED", "Вы должны быть друзьями, чтобы общаться.")
    return room


@database_sync_to_async
def connect_user(room, user):
    # add user to connected_users list
    account = Account.objects.get(pk=user.id)
    return room.connect_user(account)


@database_sync_to_async
def disconnect_user(room, user):
    # remove from connected_users list
    account = Account.objects.get(pk=user.id)
    return room.disconnect_user(account)