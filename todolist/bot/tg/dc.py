from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config, Undefined
from typing import Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class MessageFrom:
    """Отправитель сообщения"""

    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = None
    added_to_attachment_menu: Optional[bool] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Chat:
    """Чат"""

    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Message:
    """Сообщение"""

    message_id: int
    message_from: MessageFrom = field(metadata=config(field_name='from'))
    date: int
    chat: Chat
    text: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Update:
    """Входящее обновление"""

    update_id: int
    message: Optional[Message] = None
    edited_message: Optional[Message] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class GetUpdatesResponse:
    """Ответ API на метод 'getUpdates'"""

    ok: bool
    result: list[Update]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class SendMessageResponse:
    """Ответ API на метод 'sendMessage'"""

    ok: bool
    result: Message


GetUpdatesResponseSchema = GetUpdatesResponse.schema()
SendMessageResponseSchema = SendMessageResponse.schema()
