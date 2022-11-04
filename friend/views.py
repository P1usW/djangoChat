from django.shortcuts import render, redirect
from django.contrib import messages

from .models import Account, FriendRequest, FriendList

from django.http import HttpResponse
import json


def friend_list_view(request):
    try:
        account = FriendList.objects.prefetch_related('friends').get(user=request.user)
        friend_list = account.friends.all()
        context = {'friend_list': friend_list,
                   'account': account,
                   }
        return render(request, template_name='friend/friend_list_view.html', context=context)
    except FriendList.DoesNotExist:
        messages.error(request, 'Вы не можете просматривать список друхеуй несуществующего пользователя')
        return redirect('home')


def friend_request_view(request):
    user = request.user
    if not user.is_authenticated:
        messages.info(request, 'Войдите в профиль, чтобы просматривать заявки в друзья')
        return redirect('login')
    friend_requests_all = FriendRequest.objects.prefetch_related('sender').filter(receiver=user.pk, is_active=True)
    friend_requests_accounts = [user.sender for user in friend_requests_all]
    context = {
        'friend_requests_accounts': friend_requests_accounts,
    }
    return render(request, template_name='friend/friend_request_view.html', context=context)


def send_friend_request(request):
    """
    Если заявка отправлена: 1
    Если заявка отправлена, но ждёт ответа: 0
    Произошла ошибка: -1
    """
    user = request.user
    payload = {}
    if request.method == 'POST' and user.is_authenticated:
        user_id = request.POST.get('receiver_user_id')
        if user_id:
            receiver = Account.objects.get(pk=user_id)
            try:
                friend_request = FriendRequest.objects.get(sender=user, receiver=receiver)
                if friend_request.is_active:
                    payload['response'] = '0'
                else:
                    friend_request.is_active = True
                    friend_request.save()
                    payload['response'] = '1'
            except FriendRequest.DoesNotExist:
                FriendRequest.objects.create(sender=user, receiver=receiver)
                payload['response'] = '1'
        else:
            payload['response'] = '-1'
    else:
        payload['response'] = '-1'
    return HttpResponse(json.dumps(payload), content_type="application/json")


def cancel_friend_request(request, *args, **kwargs):
    """
    Если заявка отменена: 1
    Если заявки не было: 0
    Произошла ошибка: -1
    """
    user = request.user
    payload = {}
    if request.method == "POST" and user.is_authenticated:
        user_id = request.POST.get("receiver_user_id")
        if user_id:
            receiver = Account.objects.get(pk=user_id)
            try:
                friend_requests = FriendRequest.objects.get(sender=user, receiver=receiver, is_active=True)
                friend_requests.cancel()
                payload['response'] = "1"
            except FriendRequest.DoesNotExist:
                payload['response'] = "0"
        else:
            payload['response'] = "-1"
    else:
        payload['response'] = "-1"
    return HttpResponse(json.dumps(payload), content_type="application/json")


def accept_friend_request(request):
    user = request.user
    payload = {}
    if request.method == 'POST' and user.is_authenticated:
        account_id = request.POST.get('account_id')
        if account_id:
            try:
                friend_request = FriendRequest.objects.get(sender_id=account_id)
                if friend_request.receiver == user:
                    friend_request.accept()
                    payload['response'] = 'accept'
                else:
                    payload['response'] = 'error'
            except FriendRequest.DoesNotExist:
                payload['response'] = 'error'
        else:
            payload['response'] = 'error'
    else:
        payload['error'] = 'error'
    return HttpResponse(json.dumps(payload), content_type='application/json')


def decline_friend_request(request):
    user = request.user
    payload = {}
    if request.method == 'POST' and user.is_authenticated:
        account_id = request.POST.get('account_id')
        if account_id:
            try:
                friend_request = FriendRequest.objects.get(sender_id=account_id)
                if friend_request.receiver == user:
                    friend_request.decline()
                    payload['response'] = 'decline'
                else:
                    payload['response'] = 'error'
            except FriendRequest.DoesNotExist:
                payload['response'] = 'error'
        else:
            payload['response'] = 'error'
    else:
        payload['error'] = 'error'
    return HttpResponse(json.dumps(payload), content_type='application/json')


def delete_friend(request):
    user = request.user
    payload = {}
    if request.method == 'POST' and user.is_authenticated:
        friend_id = request.POST.get('friend_id')
        if friend_id:
            try:
                friend = Account.objects.get(pk=friend_id)
                friend_friend_list = FriendList.objects.get(user=friend)
                friend_friend_list.remove_friend(user)

                user_friend_list = FriendList.objects.get(user=user)
                user_friend_list.remove_friend(friend)
                payload['response'] = 'deleted'
            except Account.DoesNotExist:
                payload['response'] = 'error'
        else:
            payload['response'] = 'error'
    else:
        payload['response'] = 'error'
    return HttpResponse(json.dumps(payload), content_type='application/json')
