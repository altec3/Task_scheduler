from datetime import datetime

from django.conf import settings
from django.utils import timezone


class BaseTestCase:

    @staticmethod
    def datetime_to_str(date_time: datetime):
        return timezone.localtime(date_time).strftime(settings.REST_FRAMEWORK['DATETIME_FORMAT'])
