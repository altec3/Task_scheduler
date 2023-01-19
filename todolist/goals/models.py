from django.db import models

from core.models import User


class Category(models.Model):
    title = models.CharField(verbose_name="Название", max_length=255)
    author = models.ForeignKey(User, verbose_name="Автор", related_name="categories", on_delete=models.PROTECT)
    is_deleted = models.BooleanField(verbose_name="Удалена", default=False)
    created = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    updated = models.DateTimeField(verbose_name="Дата последнего обновления", auto_now=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title
