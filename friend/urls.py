from django.urls import path
from . import views


urlpatterns = [
    path('list', views.friend_list_view, name='list'),
    path('list_request', views.friend_request_view, name='list_request'),

    path('send_friends_request', views.send_friend_request, name='send_friend_request'),
    path('cancel_friends_request', views.cancel_friend_request, name='cancel_friend_request'),
]
