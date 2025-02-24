import datetime
from pydantic import BaseModel, Field
from typing import Optional, List


class TelegramBase(BaseModel):
    id: int
    type: Optional[str] = None

class TelegramChannel(TelegramBase):
    title: Optional[str] = None
    name: Optional[str] = None
    participants_count: Optional[int] = None
    description: Optional[str] = None
    messages: list = Field(default_factory=list)
    users: list = Field(default_factory=list)

class Photo(BaseModel):
    date: datetime.datetime
    data: Optional[str] = None

class TelegramUser(TelegramBase):
    user_hash: Optional[int] = None
    username: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phone: Optional[str] = None
    bot: Optional[bool] = None
    photos: List[Photo] = []
    user_was_online: Optional[str] = None

class TelegramMessage(TelegramBase):
    sender: Optional[TelegramUser] = None
    date: datetime.datetime
    forward_from: Optional[str] = None
    reply_to_msg_id: Optional[int]
    views: Optional[int] = None
    content: Optional[str] = None
    replies: list = Field(default_factory=list)
    data:Optional[bytes] = None
    file_name: Optional[str] = None