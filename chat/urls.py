from django.urls import path

from . import views

urlpatterns = [
    path('', views.chat_search, name='chat_search'),
    path('<str:room_name>/', views.chat_room, name='chat_room'),
    path('private_chat', views.private_chat_room_view, name='private_chat')
]