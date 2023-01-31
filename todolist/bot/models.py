from django.db import models

from core.models import User


class TgUser(models.Model):

    tg_id = models.SmallIntegerField(verbose_name='ID пользователя в Telegram')
    tg_username = models.CharField(verbose_name='Имя пользователя в Telegram', max_length=255, null=True, blank=True)
    verification_code = models.CharField(verbose_name='Код верификации', max_length=255)
    user = models.ForeignKey(User, verbose_name='Пользователь', related_name='tg_user', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Telegram пользователь'
        verbose_name_plural = 'Telegram пользователи'

    def __str__(self):
        return self.user.username
