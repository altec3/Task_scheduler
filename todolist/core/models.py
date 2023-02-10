from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Модель пользователя проекта 'todolist'"""

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username
