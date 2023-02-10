import random
import string

from bot.models import TgUser, TgChatState
from bot.tg.client import TgClient
from goals.models import Goal, Category


class BaseStateClass:
    """Базовый класс для классов состояний чата

    Args:
        tg_user: Telegram пользователь. Предоставляет доступ к атрибутам пользователя.
        tg_client: Telegram клиент. Предоставляет доступ к функциям получения входящих обновлений
            и отправки сообщений.
    """

    def __init__(self, tg_user: TgUser, tg_client: TgClient):
        self._tg_user = tg_user
        self.__tg_client = tg_client

        #: str: Текст приветствия бота
        self._text: str | None = None

        #: list of string: Список разрешенных в чате команд
        self._allowed_commands: list = ['/start', '/goals', '/create', '/cancel']

        #: dict: Словарь с вариантами сообщений бота
        self._messages = {
            'allowed_commands': 'Для продолжения отправьте одну из команд:\n'
                                '/goals - просмотреть все цели;\n'
                                '/create - создать цель;\n'
                                '/cancel - отменить создание цели.',
            'unknown_command': '[unknown command]\n',
            'verification_required': 'Для продолжения необходимо пройти верификацию.',
            'select_category': 'Отправьте название категории, в которой будет создана цель:\n',
            'goal_title': 'Отправьте название цели.',
            'successful': '[successful]',
            'failure': '[failure]',
        }

    @staticmethod
    def __generate_verification_code(length: int = 16) -> str:
        symbols = string.ascii_letters + string.digits
        code = ''.join(random.sample(symbols, length))
        return code

    def get_verification_code(self) -> str:
        """Возвращает строку из случайных чисел и букв

        Returns:
             str: последовательность из чисел и букв
        """
        code = self.__generate_verification_code()

        tg_user = self._tg_user
        tg_user.verification_code = code
        tg_user.save(update_fields=('verification_code',))
        return code

    def _send_message(self, text: str) -> None:
        self.__tg_client.send_message(chat_id=self._tg_user.tg_id, text=text)

    def run_actions(self) -> None:
        """Выполняет характерные для определенного состояния действия"""

        self._send_message(text=self._text)
        self._send_message(text=self.get_verification_code())


class NewState(BaseStateClass):
    """Класс состояния чата: пользователь не известен

    Args:
        tg_user: Telegram пользователь. Предоставляет доступ к атрибутам пользователя.
        tg_client: Telegram клиент. Предоставляет доступ к функциям получения входящих обновлений
            и отправки сообщений.
    """

    def __init__(self, tg_user: TgUser, tg_client: TgClient):
        super().__init__(tg_user, tg_client)

        #: str: Текст приветствия бота
        self._text = 'Привет! Я Telegram бот проекта \"TodoList\"\n'+self._messages['verification_required']


class NotVerifiedState(BaseStateClass):
    """Класс состояния чата: пользователь не верифицирован

    Args:
        tg_user: Telegram пользователь. Предоставляет доступ к атрибутам пользователя.
        tg_client: Telegram клиент. Предоставляет доступ к функциям получения входящих обновлений
            и отправки сообщений.
    """
    def __init__(self, tg_user: TgUser, tg_client: TgClient):
        super().__init__(tg_user, tg_client)

        #: str: Текст приветствия бота
        self._text = 'С возвращением!\n'+self._messages['verification_required']


class VerifiedState(BaseStateClass):
    """Класс состояния чата: пользователь прошел верификацию

    Args:
        tg_user: Telegram пользователь. Предоставляет доступ к атрибутам пользователя.
        tg_client: Telegram клиент. Предоставляет доступ к функциям получения входящих обновлений
            и отправки сообщений.
    """
    def __init__(self, tg_user: TgUser, tg_client: TgClient, chat_msg: str = None):
        super().__init__(tg_user, tg_client)
        self.__chat_msg = chat_msg
        self.__chat_state, _ = TgChatState.objects.get_or_create(tg_user=tg_user)

    def run_actions(self) -> None:
        """Выполняет характерные для определенного состояния действия"""

        #: bool: Флаг выполнения команды /create
        is_create_command = self.__chat_state.is_create_command

        if self.__chat_msg == '/create':
            self.__chat_state.is_create_command = True
            self.__chat_state.save(update_fields=('is_create_command',))

            categories: list = Category.objects.all().filter(
                user_id=self._tg_user.user_id,
                is_deleted=False
            ).values_list('title', flat=True)

            self._send_message(
                text=self._messages['select_category'] + '\n'.join(categories) if categories
                else '[categories not found]'
            )

        if not is_create_command:
            if self.__chat_msg not in self._allowed_commands:
                self._send_message(text=self._messages['unknown_command']+self._messages['allowed_commands'])

            if self.__chat_msg == '/start':
                self._send_message(text=self._messages['allowed_commands'])

            if self.__chat_msg == '/goals':
                goals: list = Goal.objects.all().filter(
                    category__board__participants__user_id=self._tg_user.user_id,
                    category__is_deleted=False,
                    status__lt=Goal.Status.archived,
                ).values_list('title', flat=True)

                self._send_message(text='\n'.join(goals) if goals else '[goals not found]')

        elif self.__chat_msg == '/cancel':
            self.__chat_state.set_default()
            self._send_message(text=self._messages['successful'])

        else:
            if not self.__chat_state.category_id:
                categories: list = Category.objects.all().filter(
                    user_id=self._tg_user.user_id,
                    is_deleted=False
                ).values_list('title', flat=True)

                if self.__chat_msg not in categories:
                    self._send_message(
                        text=self._messages['select_category'] + '\n'.join(categories) if categories
                        else '[categories not found]'
                    )
                else:
                    category = Category.objects.all().filter(user_id=self._tg_user.user_id).get(title=self.__chat_msg)
                    self.__chat_state.category_id = category.id
                    self.__chat_state.save(update_fields=('category_id',))
                    self._send_message(text=self._messages['goal_title'])
            else:
                goal = Goal.objects.create(
                    user_id=self._tg_user.user_id,
                    category_id=self.__chat_state.category_id,
                    title=self.__chat_msg
                )
                if goal.id:
                    self.__chat_state.set_default()
                    self._send_message(text=self._messages['successful'])
                else:
                    self._send_message(text=self._messages['failure'])
