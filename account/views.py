from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.conf import settings
from django.urls import reverse

from urllib.parse import urlencode

from .forms import UserRegister, UserLogin, ProfileEdit, PasswordEdit
from .models import Account
from friend.models import FriendList, FriendRequest


def profile_view(request, username):
    """
    1 - друг
    2 - не друг отправил заявку
    3 - не друг не отправил заявку
    4 - ошибка
    """
    context = {}
    account = get_object_or_404(Account, username=username)
    if (user := request.user) != account:
        context['account'] = account
        try:
            friend_list = FriendList.objects.get(user=user)
            if account in friend_list.friends.all():
                context['check_request'] = 1
            else:
                try:
                    friend_request = FriendRequest.objects.get(sender=user, receiver=account)
                    if friend_request.is_active:
                        context['check_request'] = 2
                    else:
                        context['check_request'] = 3
                except FriendRequest.DoesNotExist:
                    context['check_request'] = 3
        except FriendList.DoesNotExist:
            context['check_request'] = 4
    else:
        context['account'] = user
    return render(request, template_name='account/profile_view.html', context=context)


def profile_edit_view(request, *args, **kwargs):
    if not request.user.is_authenticated:
        base_url = reverse('login')
        add_next = urlencode({'next': '/edit'})
        url = f'{base_url}?{add_next}'
        return redirect(url)

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
        base_url = reverse('login')
        add_next = urlencode({'next': '/security'})
        url = f'{base_url}?{add_next}'
        return redirect(url)

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
        form = UserLogin(request, request.POST)
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
