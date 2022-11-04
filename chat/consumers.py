from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.paginator import Paginator
from account.models import Account

import json

from friend.models import FriendList
from .models import PrivateChatRoom, PrivateRoomChatMessage
from .exceptions import ClientError
from .utils import LazyRoomChatMessageEncoder


class AsyncChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_id = 'chat_%s' % self.room_id

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_id,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_id,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.scope['user'].username
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_id,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            })

    # Receive message from room group
    async def chat_message(self, event):

        message = event['username'] + ': ' + event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


class PrivateAsyncChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = int(self.scope['url_route']['kwargs']['room_id'])
        try:
            self.room = await get_room_or_error(self.room_id, self.scope["user"])
        except ClientError as e:
            return await self.handle_client_error(e)
        self.group_name = self.room.group_name

        await self.join_room(self.room_id)

        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        text_data = json.loads(text_data)
        command = text_data.get('command', None)
        if command == 'send_message':
            print('Send message')
            await self.chat_message(text_data['message'])
        elif command == 'get_chat_messages':
            print('Get all messages')
            all_messages = await get_chat_messages(self.room, text_data['page_number'])
            await self.send(json.dumps(all_messages))
        elif command == None:
            print('None')

    async def disconnect(self, code):
        print("ChatConsumer: disconnect")
        try:
            await self.leave_room(self.room_id)
        except Exception as e:
            print("EXCEPTION: " + str(e))
            pass

    async def join_room(self, room_id):
        print("ChatConsumer: join_room: " + str(room_id))

        # Add user to "users" list for room
        await connect_user(self.room, self.scope["user"])

        # Add them to the group so they get room messages
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        # # Instruct their client to finish opening the room
        # await self.send({
        #     "join": str(self.room_id),
        # })

    async def leave_room(self, room_id):
        print("ChatConsumer: leave_room: " + str(room_id))

        await disconnect_user(self.room, self.scope["user"])

        # Remove them from the group so they no longer get room messages
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )

        # # Instruct their client to finish closing the room
        # await self.send({
        #     "leave": str(self.room_id),
        # })

    async def chat_message(self, event):
        room_message = await create_room_chat_messages(self.room, self.scope['user'], event)
        # Send message to WebSocket
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'send_room',
                'payload': room_message,
            })

    async def send_room(self, event):
        await self.send(text_data=json.dumps(event['payload']))

    async def handle_client_error(self, e):
        """
        Called when a ClientError is raised.
        Sends error data to UI.
        """
        errorData = {}
        errorData['error'] = e.code
        if e.message:
            errorData['message'] = e.message
            await self.send(errorData)
        return


@database_sync_to_async
def create_room_chat_messages(room, user, messages):
    qs = PrivateRoomChatMessage.objects.create(user=user, room=room, content=messages)
    payload = {
        'type_messages': 1,
        'messages': [
            {
                'msg_id': qs.pk,
                'user_id': qs.user.pk,
                'username': qs.user.username,
                'message': qs.content,
            }
        ]
    }
    return payload


@database_sync_to_async
def get_chat_messages(room, page_number=1):
    all_messages_user = PrivateRoomChatMessage.objects.by_room(room)
    p = Paginator(all_messages_user, 20)
    s = LazyRoomChatMessageEncoder()
    if p.num_pages > page_number:
        payload = {
            'type_messages': 3,
        }
        return payload
    else:
        payload = {
            'type_messages': 2,
            'messages': s.serialize(p.page(page_number).object_list)
        }
        return payload


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
