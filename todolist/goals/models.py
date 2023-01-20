from django.db import models

from core.models import User


class Category(models.Model):
    title = models.CharField(verbose_name='Название', max_length=255)
    author = models.ForeignKey(User, verbose_name='Автор', related_name='categories', on_delete=models.PROTECT)
    is_deleted = models.BooleanField(verbose_name='Удалена', default=False)
    created = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Дата последнего обновления', auto_now=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Goal(models.Model):

    class Status(models.IntegerChoices):
        to_do = 1, 'К выполнению'
        in_progress = 2, 'В процессе'
        done = 3, 'Выполнено'
        archived = 4, 'Архив'

    class Priority(models.IntegerChoices):
        low = 1, 'Низкий'
        medium = 2, 'Средний'
        high = 3, 'Высокий'
        critical = 4, 'Критический'

    author = models.ForeignKey(User, verbose_name='Автор', related_name='goals', on_delete=models.PROTECT)
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='goals', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Заголовок', max_length=255)
    description = models.TextField(verbose_name='Описание', max_length=1000)
    status = models.PositiveSmallIntegerField(verbose_name='Статус', choices=Status.choices, default=Status.to_do)
    priority = models.PositiveSmallIntegerField(
        verbose_name='Приоритет', choices=Priority.choices, default=Priority.medium
    )
    created = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Дата последнего обновления', auto_now=True)
    due_date = models.DateTimeField(verbose_name='Дедлайн')

    class Meta:
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'

    def __str__(self):
        return self.title
