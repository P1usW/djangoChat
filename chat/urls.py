from django.urls import path

from . import views

urlpatterns = [
    path('', views.chat_search, name='chat_search'),
    path('<str:room_name>/', views.chat_room, name='chat_room'),
    path('all_private_chat', views.all_private_chat_room_view, name='all_private_chat'),
    path('private_chat/friend=<int:user_id>', views.private_chat_room_view, name='private_chat'),
    path('create_or_return_private_chat/', views.create_or_return_private_chat, name='create-or-return-private-chat'),
]