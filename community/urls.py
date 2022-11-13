from django.urls import path

from . import views

urlpatterns = [
    path('', views.all_groups_view, name='groups'),
    path('<str:uniq_name>', views.group_view, name='group')
]
