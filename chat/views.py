from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from django.db.models import Q
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


def chat_room(request, room_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Ввойдите в систему, чтобы присоединиться к чату')
        base_url = reverse('login')
        add_next = urlencode({'next': f'/chat/{room_id}'})
        url = f'{base_url}?{add_next}'
        return redirect(url)

    return render(request, 'chat/chat_room.html', {
        'room_id_json': room_id,
    })


def private_chat_room_view(request, user_id):
    user = request.user
    friend = Account.objects.get(pk=user_id)

    if not request.user.is_authenticated:
        messages.error(request, 'Ввойдите в систему, чтобы присоединиться к чату')
        base_url = reverse('login')
        add_next = urlencode({'next': '/security'})
        url = f'{base_url}?{add_next}'
        return redirect(url)

    try:
        friend_list = FriendList.objects.get(user=user)
        if not friend_list.is_mutual_fiend(friend):
            return redirect('list')
    except FriendList.DoesNotExist:
        return redirect('home')

    try:
        room = PrivateChatRoom.objects.get(user1=user, user2=friend)
    except PrivateChatRoom.DoesNotExist:
        try:
            room = PrivateChatRoom.objects.get(user1=friend, user2=user)
        except PrivateChatRoom.DoesNotExist:
            room = PrivateChatRoom(user1=user, user2=friend, is_active=True)
            room.save()

    context = {
        'friend': friend,
        'room': room,
    }
    return render(request, template_name='chat/private_chat_room.html', context=context)


def all_private_chat_room_view(request):
    context = {}
    user = request.user
    if not user.is_authenticated:
        messages.error(request, 'Ввойдите в систему, чтобы присоединиться к чату')
        base_url = reverse('login')
        add_next = urlencode({'next': f'/private_chat'})
        url = f'{base_url}?{add_next}'
        return redirect(url)

    context['m_and_f'] = get_recent_chatroom_messages(user)

    return render(request, 'chat/all_private_chat_room_view.html', context=context)


def get_recent_chatroom_messages(user):
    rooms = PrivateChatRoom.objects.prefetch_related('user1', 'user2').filter((Q(user1=user) | Q(user2=user)),
                                                                              is_active=True)
    m_and_f = []
    for room in rooms:
        if room.user1 == user:
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
                'friend': friend,
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
                payload['chat_id'] = chat.id
            except Account.DoesNotExist:
                payload['response'] = '0'
    else:
        payload['response'] = '-1'
    return HttpResponse(json.dumps(payload), content_type='application/json')
