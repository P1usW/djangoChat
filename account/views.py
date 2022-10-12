from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

from .forms import UserRegister, UserLogin, ProfileEdit, PasswordEdit
from .models import Account, FriendRequest
from django.conf import settings

from django.http import HttpResponse
import json


def profile_view(request, username):
    context = {}
    account = get_object_or_404(Account, username=username)
    if user := request.user != account:
        try:
            friend_request = FriendRequest.objects.get(sender=user, receiver=account)
            print(friend_request)
            if friend_request.is_active:
                context['check_request'] = True
            else:
                context['check_request'] = False
        except FriendRequest.DoesNotExist:
            context['check_request'] = False
    context['account'] = account
    return render(request, template_name='account/profile_view.html', context=context)


def friend_list_view(request, username):
    account = Account.objects.filter(username=username).select_related('user').get()
    friend_list = account.user.friends.all()
    context = {'friend_list': friend_list}
    return render(request, template_name='account/friend_list_view.html', context=context)


def friend_request_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'Войдите в профиль, чтобы просматривать заявки в друзья')
        return redirect('login')
    try:
        friend_request = FriendRequest.objects.get(receiver=request.user)
    except FriendRequest.DoesNotExist:
        friend_request = False
    context = {
        'friend_request': friend_request,
    }
    if friend_request:
        return render(request, template_name='', context=context)


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
                # There should only ever be ONE active friend request at any given time. Cancel them all just in case.
                # found the request. Now cancel it
                friend_requests.cancel()
                payload['response'] = "1"
            except FriendRequest.DoesNotExist:
                payload['response'] = "0"
        else:
            payload['response'] = "-1"
    else:
        # should never happen
        payload['response'] = "-1"
    return HttpResponse(json.dumps(payload), content_type="application/json")


def profile_edit_view(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect('login')

    username = request.user.username
    user = Account.objects.get(username=username)

    if request.method == 'POST':
        form = ProfileEdit(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные успешно изменены.')
            if redirect_url := request.GET.get('next'):
                return redirect(redirect_url)
            return redirect('profile', username=form.cleaned_data['username'])
        else:
            form = ProfileEdit(request.POST, instance=user,
                               initial={
                                   'username': user.username,
                                   'email': user.email,
                                   'first_name': user.first_name,
                                   'last_name': user.last_name,
                                   'profile_image': user.profile_image,
                                   'about_me': user.about_me,
                                   'facebook': user.facebook,
                                   'twitter': user.twitter,
                                   'instagram': user.instagram,
                               }
                               )
            context = {'form': form}
            messages.error(request, 'Произошла ошибка, повторите снова!')
    else:
        form = ProfileEdit(
            initial={
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'profile_image': user.profile_image,
                'about_me': user.about_me,
                'facebook': user.facebook,
                'twitter': user.twitter,
                'instagram': user.instagram,
            }
        )
        context = {'form': form}
    context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
    return render(request, template_name='account/profile_edit_view.html', context=context)


def password_edit_view(request):
    if not request.user.is_authenticated:
        redirect('login')

    if request.method == 'POST':
        form = PasswordEdit(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные успешно изменены.')
            if redirect_url := request.GET.get('next'):
                return redirect(redirect_url)
            return redirect('profile', username=request.user.username)
        else:
            form = PasswordEdit(data=request.POST, user=request.user)
            context = {'form': form}
            messages.error(request, 'Произошла ошибка, повторите снова!')
    else:
        form = PasswordEdit(user=request.user)
        context = {'form': form}

    return render(request, template_name='account/password_edit_view.html', context=context)


def home_view(request):
    context = {}
    return render(request, template_name='account/home_view.html', context=context)


def profile_search(request, *args, **kwargs):
    context = {}
    username = request.GET.get('search')
    acoounts = Account.objects.filter(username__contains=username)

    if acoounts:
        context['accounts'] = acoounts
    return render(request, template_name='account/search.html', context=context)


def register_view(request, *args, **kwargs):
    user = request.user
    context = {}

    if user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegister(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'Аккаунт успешно зарегестрирован!')
            if redirect_url := request.GET.get('next'):
                return redirect(redirect_url)
            return redirect('home')
        else:
            messages.error(request, 'Произошла ошибка, повторите снова!')
            context['form'] = form
    else:
        form = UserRegister()
        context['form'] = form

    return render(request, template_name='account/register_view.html', context=context)


def login_view(request, *args, **kwargs):
    user = request.user
    context = {}

    if user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserLogin(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Вы успешно вошли в систему.')
                if redirect_url := request.GET.get('next'):
                    return redirect(redirect_url)
                return redirect('home')
        else:
            messages.error(request, 'Произошла ошибка, повторите снова!')
            context['form'] = form
    else:
        form = UserLogin()
        context['form'] = form

    return render(request, template_name='account/login_view.html', context=context)


def logout_view(request):
    if not request.user.is_authenticated:
        return redirect('home')

    logout(request)
    return redirect('home')
