import json

from django.shortcuts import render
from django.utils.safestring import mark_safe


def chat_search(request):
    """Главная страница"""
    return render(request, 'chat/chat_search.html', {})


def chat_room(request, room_name):
    """"""
    return render(request, 'chat/chat_room.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })