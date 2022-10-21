from django import template


register = template.Library()


@register.inclusion_tag('chat/chat_view_tag.html')
def show_room(room_info):
    messages, friend = room_info.values()
    return {
        'messages': messages,
        'friend': friend,
    }
