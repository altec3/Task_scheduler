from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config, Undefined
from typing import Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class MessageFrom:
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
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Message:
    message_id: int
    message_from: MessageFrom = field(metadata=config(field_name='from'))
    date: int
    chat: Chat
    text: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Update:
    update_id: int
    message: Optional[Message] = None
    edited_message: Optional[Message] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class GetUpdatesResponse:
    ok: bool
    result: list[Update]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class SendMessageResponse:
    ok: bool
    result: Message


GetUpdatesResponseSchema = GetUpdatesResponse.schema()
SendMessageResponseSchema = SendMessageResponse.schema()
