from django.contrib import admin

from bot.models import TgUser, TgChatState


@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    """Регистрация модели TgUser для отображения в панели администратора"""

    list_display = ('tg_id', 'tg_username', 'user',)
    search_fields = ('user',)


@admin.register(TgChatState)
class TgChatStateAdmin(admin.ModelAdmin):
    """Регистрация модели TgChatState для отображения в панели администратора"""

    list_display = ('tg_user', 'category', 'is_create_command',)
    search_fields = ('tg_user',)
