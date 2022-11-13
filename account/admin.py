from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .models import Account, SupportMessages


@admin.register(Account)
class AccountAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'date_joined', 'get_photo')
    list_display_links = ('username',)
    search_fields = ('username', 'first_name', 'last_name')
    readonly_fields = ('date_joined', )

    @admin.display(description='Фотография')
    def get_photo(self, obj):
        if obj.profile_image:
            return mark_safe(f'<img src="{obj.profile_image.url}" width="75"')
        else:
            return '-'


@admin.register(SupportMessages)
class SupportMessagesAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'user')
    search_fields = ('title',)
