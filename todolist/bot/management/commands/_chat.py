from bot.management.commands._states import BaseStateClass, NewState, NotVerifiedState, VerifiedState
from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.dc import Message


class Chat:

    def __init__(self, message: Message):
        self.__message = message
        self.__state: BaseStateClass | None = None

    @property
    def state(self):
        if self.__state:
            return self.__state
        raise RuntimeError('state does not set')

    def set_state(self, tg_client: TgClient):
        """
        Устанавливает текущее состояние чата:
            NewState - пользователь не известен;
            NotVerifiedState - пользователь не верифицирован;
            VerifiedState - пользователь прошел верификацию
        """
        tg_user, created = TgUser.objects.get_or_create(
            tg_id=self.__message.message_from.id,
            tg_username=self.__message.message_from.username
        )

        if created:
            self.__state = NewState(tg_user=tg_user, tg_client=tg_client)
        else:
            if not tg_user.user_id:
                self.__state = NotVerifiedState(tg_user=tg_user, tg_client=tg_client)
            else:
                self.__state = VerifiedState(tg_user=tg_user, tg_client=tg_client, chat_msg=self.__message.text)
