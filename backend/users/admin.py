from django.contrib import admin

from .models import Subscription, User


@admin.register(User)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'email', 'username', 'first_name', 'last_name', 'is_subscribed'
    )
    list_display_links = ('email', 'username')
    search_fields = ('email', 'username')
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')
    list_filter = ('user', 'author')
