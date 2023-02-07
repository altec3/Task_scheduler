import logging

from django.core.management import BaseCommand

from bot.management.commands._chat import Chat
from bot.tg.client import TgClient
from todolist import settings


class Command(BaseCommand):
    help = 'Runs Telegram bot'

    def __init__(self):
        super().__init__()
        self.tg_client = TgClient(token=settings.TG_TOKEN)
        self.logger = logging.getLogger(__name__)
        self.logger.info('Bot start pooling')

    def handle(self, *args, **options):
        offset = 0
        while True:
            response = self.tg_client.get_updates(offset=offset)
            for item in response.result:
                offset = item.update_id + 1
                # Старт чата
                self.logger.info(item.message)
                if item.message:
                    chat = Chat(message=item.message)
                    # Инициализация текущего состояния чата
                    chat.set_state(tg_client=self.tg_client)
                    # Выполнение действий для текущего состояния
                    chat.state.run_actions()
