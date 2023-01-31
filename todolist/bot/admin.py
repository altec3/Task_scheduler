from django.contrib import admin

from bot.models import TgUser


@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    list_display = ('tg_id', 'tg_username', 'user',)
    search_fields = ('user',)
