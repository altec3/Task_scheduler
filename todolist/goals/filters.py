import django_filters
from django.db import models

from goals.models import Goal


class GoalsFilter(django_filters.rest_framework.FilterSet):
    """Фильтр для целей

    Реализует фильтрацию целей по дате дедлайна, категории, статусу, приоритету
    """
    class Meta:
        model = Goal
        fields = {
            'due_date': ('lte', 'gte'),
            'category': ('exact', 'in'),
            'status': ('exact', 'in'),
            'priority': ('exact', 'in'),
        }

    filter_overrides = {
        models.DateTimeField: {'filter_class': django_filters.IsoDateTimeFilter},
    }
