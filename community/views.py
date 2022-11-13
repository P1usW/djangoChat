from django.shortcuts import render, redirect
from django.urls import reverse

from urllib.parse import urlencode

from .models import Group, Post


def all_groups_view(request):
    user = request.user
    context = {}

    if not request.user.is_authenticated:
        base_url = reverse('login')
        add_next = urlencode({'next': '/edit'})
        url = f'{base_url}?{add_next}'
        return redirect(url)

    groups = Group.objects.filter(subscribers=user)
    context['groups'] = groups
    return render(request, 'community/all_groups_view.html', context)


def group_view(request, uniq_name):

    try:
        group = Group.objects.prefetch_related('posts', 'subscribers', 'moderators').get(uniq_name_url=uniq_name)
        posts = group.posts.prefetch_related('user_author').order_by('-timestamp').all()
    except Group.DoesNotExist:
        raise
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, 'community/group_view.html', context)
