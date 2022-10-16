from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .models import Account


@admin.register(Account)
class AccountAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'date_joined', 'get_photo')
    list_display_links = ('username',)
    search_fields = ('username', 'first_name', 'last_name')
    readonly_fields = ('date_joined', )

    @admin.display(description='Фотография')
    def get_photo(self, obj):
        if obj.profile_image:
            return mark_safe('<img scr="{}" width=70'.format(obj.profile_image.url))
        else:
            return '-'
