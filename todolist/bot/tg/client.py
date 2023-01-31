import requests

from bot.tg.dc import GetUpdatesResponse, SendMessageResponse, SendMessageResponseSchema, GetUpdatesResponseSchema


class TgClient:
    def __init__(self, token: str):
        self.token = token

    def get_url(self, method: str):
        return f'https://api.telegram.org/bot{self.token}/{method}'

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        url = self.get_url(method='getUpdates')
        response = requests.get(
            url=url,
            params={'offset': offset, 'timeout': timeout}
        )

        return GetUpdatesResponseSchema.load(response.json())

    def send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        url = self.get_url(method='sendMessage')
        response = requests.get(
            url=url,
            params={'chat_id': chat_id, 'text': text}
        )

        return SendMessageResponseSchema.load(response.json())
