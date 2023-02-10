import requests
from requests import exceptions

from bot.tg.dc import GetUpdatesResponse, SendMessageResponse, SendMessageResponseSchema, GetUpdatesResponseSchema


class TgClient:
    """Telegram клиент

    Args:
        token (str): токен для доступа к Telegram API
    """
    def __init__(self, token: str):
        self.token = token

    def get_url(self, method: str) -> str:
        """Возвращает URL для доступа к Telegram API

        Args:
            method (str): метод Telegram API
        Returns:
             str: URL
        """
        return f'https://api.telegram.org/bot{self.token}/{method}'

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        """Реализует метод 'getUpdates' API для получения входящих обновлений

        Args:
            offset (int): идентификатор первого возвращаемого обновления
            timeout (int): таймаут в секундах при использовании long polling - должен быть больше нуля
        Returns:
             массив объектов класса Update, содержащий атрибуты принятого сообщения
        """
        url = self.get_url(method='getUpdates')
        try:
            response = requests.get(
                url=url,
                params={'offset': offset, 'timeout': timeout}
            )
        except exceptions.RequestException:
            raise exceptions.RequestException
        else:
            return GetUpdatesResponseSchema.load(response.json())

    def send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        """Реализует метод 'sendMessage' API для отправки сообщения участникам чата

        Args:
            chat_id (int): идентификатор чата или имя пользователя целевого чата
            text (str): текст сообщения
        Returns:
             объект класса Message, содержащий атрибуты отправленного сообщения
        """
        url = self.get_url(method='sendMessage')
        try:
            response = requests.get(
                url=url,
                params={'chat_id': chat_id, 'text': text}
            )
        except exceptions.RequestException:
            raise exceptions.RequestException
        else:
            return SendMessageResponseSchema.load(response.json())
