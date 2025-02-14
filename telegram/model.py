import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class TelegramChannel(BaseModel):
    id: int
    messages: list = Field(default_factory=list)
    users: list = Field(default_factory=list)

class Photo(BaseModel):
    date: datetime.datetime
    data: Optional[str] = None

class TelegramUser(BaseModel):
    id:int
    user_hash: Optional[int] = None
    username: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phone: Optional[str] = None
    bot: Optional[bool] = None
    photos: List[Photo] = []

class TelegramMessage(BaseModel):
    id: int
    sender: Optional[TelegramUser] = None
    date: datetime.datetime
    forward: Optional[str] = None
    reply_to_msg_id: Optional[int]
    views: Optional[int] = None
    content: Optional[str] = None
    replies: list = Field(default_factory=list)
    data:Optional[bytes] = None
    file_name: Optional[str] = None