from django.urls import path
from . import views


urlpatterns = [
    path('', views.home_view, name='home'),
    path('register', views.register_view, name='register'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('edit', views.profile_edit_view, name='edit'),
    path('security', views.password_edit_view, name='security'),
    path('friends/<str:username>', views.friend_list_view, name='friend_list'),

    path('send_friends_request', views.send_friend_request, name='send_friend_request'),
    path('cancel_friends_request', views.cancel_friend_request, name='cancel_friend_request'),

    path('search', views.profile_search, name='search'),
    path('<str:username>', views.profile_view, name='profile'),
]
