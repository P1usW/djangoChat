from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.http import HttpResponse
from account.models import Account
from friend.models import FriendList

import json
import pytz
from datetime import datetime
from itertools import chain
from urllib.parse import urlencode

from .utils import find_or_create_private_chat
from .models import PrivateChatRoom, PrivateRoomChatMessage


def chat_search(request):
    return render(request, 'chat/chat_search.html', {})


def chat_room(request, room_name):
    if not request.user.is_authenticated:
        messages.error(request, 'Ввойдите в систему, чтобы присоединиться к чату')
        base_url = reverse('login')
        add_next = urlencode({'next': '/security'})
        url = f'{base_url}?{add_next}'
        return redirect(url)

    return render(request, 'chat/chat_room.html', {
        'room_name_json': mark_safe(json.dumps(room_name)),
    })


def private_chat_room_view(request):
    room_id = request.GET.get('room_id')
    user = request.user
    if not user.is_authenticated:
        messages.error(request, 'Ввойдите в систему, чтобы присоединиться к чату')
        base_url = reverse('login')
        add_next = urlencode({'next': f'/private_chat/?room_id={room_id}'})
        url = f'{base_url}?{add_next}'
        return redirect(url)

    context = {}
    context['m_and_f'] = get_recent_chatroom_messages(user)

    if room_id:
        context["room_id"] = room_id

    return render(request, 'chat/private_chat_room.html', context=context)


def get_recent_chatroom_messages(user):
    rooms1 = PrivateChatRoom.objects.filter(user1=user, is_active=True)
    rooms2 = PrivateChatRoom.objects.filter(user2=user, is_active=True)

    rooms = list(chain(rooms1, rooms2))

    m_and_f = []
    for room in rooms:
        if room.user == user:
            friend = room.user2
        else:
            friend = room.user1

        friend_list = FriendList.objects.get(user=user)
        if not friend_list.is_mutual_fiend(friend):
            chat = find_or_create_private_chat(user, friend)
            chat.is_active = False
            chat.save()
        else:
            try:
                message = PrivateRoomChatMessage.objects.filter(room=room, user=friend).latest('timestamp')
            except PrivateRoomChatMessage.DoesNotExist:
                # create a dummy message with dummy timestamp
                today = datetime(
                    year=1950,
                    month=1,
                    day=1,
                    hour=1,
                    minute=1,
                    second=1,
                    tzinfo=pytz.UTC
                )
                message = PrivateRoomChatMessage(
                    user=friend,
                    room=room,
                    timestamp=today,
                    content="",
                )
            m_and_f.append({
                'message': message,
                'friend': friend
            })
    return sorted(m_and_f, key=lambda x: x['message'].timestamp, reverse=True)


def create_or_return_private_chat(request):
    """
    1 - аккаунт существует
    0 - аккаунт не существует
    -1 - пользователь не в сети
    """
    user1 = request.user
    payload = {}
    if user1.is_authenticated:
        if request.method == 'POST':
            user2_id = request.POST.get('user2_id')
            try:
                user2 = Account.objects.get(pk=user2_id)
                chat = find_or_create_private_chat(user1, user2)
                payload['response'] = '1'
                payload['chat_if'] = chat.id
            except Account.DoesNotExist:
                payload['response'] = '0'
    else:
        payload['response'] = '-1'
    return HttpResponse(json.dumps(payload), content_type='application/json')
