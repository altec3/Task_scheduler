from django.db import models

from core.models import User
from goals.models import Category


class TgUser(models.Model):
    """Модель для реализации верификации пользователя в Telegram чате

    Сопоставляет пользователя проекта 'todolist' с пользователем Telegram чата
    """

    tg_id = models.IntegerField(verbose_name='ID пользователя в Telegram', unique=True)
    tg_username = models.CharField(verbose_name='Имя пользователя в Telegram', max_length=255, null=True, blank=True)
    verification_code = models.CharField(verbose_name='Код верификации', max_length=255, unique=True)
    user = models.ForeignKey(User,
                             verbose_name='Пользователь',
                             related_name='tg_user',
                             null=True,
                             on_delete=models.CASCADE
                             )

    class Meta:
        verbose_name = 'Telegram пользователь'
        verbose_name_plural = 'Telegram пользователи'

    def __str__(self):
        return str(self.tg_id)


class TgChatState(models.Model):
    """Модель для реализации команды /create

    Сохраняет статус команды /create и сопутствующих параметров
    """

    tg_user = models.ForeignKey(TgUser,
                                verbose_name='TG пользователь',
                                related_name='tg_chat_state',
                                on_delete=models.CASCADE
                                )
    category = models.ForeignKey(Category,
                                 verbose_name='Категория',
                                 related_name='tg_chat_state',
                                 null=True,
                                 on_delete=models.CASCADE
                                 )
    is_create_command = models.BooleanField(verbose_name='Выполняется команда /create', default=False)

    class Meta:
        verbose_name = 'Состояние чата'
        verbose_name_plural = 'Состояния чата'

    def set_default(self):
        self.category = None
        self.is_create_command = False
        self.save(update_fields=('category', 'is_create_command',))

    def __str__(self):
        return str(self.tg_user.tg_id)
