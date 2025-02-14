import requests
from telegram_base import TelegramBotBase


class TgdbBotSearch(TelegramBotBase):
    
        def __init__(self, api_id, api_hash):
            bot_username = "@tgdb_bot"
            super().__init__(session_name = "tgdb_session", api_id = api_id, api_hash = api_hash, bot_username = bot_username)
    
        def info(self, arg: str) -> str:
            return self.send_command_sync(f"/info {arg}")
        
        def channel(self, arg: str) -> str:
            return self.send_command_sync(f"/channel {arg}")
        
        def group(self, arg: str) -> str:
            return self.send_command_sync(f"/group {arg}")
        
        
class Adapter:

    def __init__(self, obj, **adapted_methods):
        self.obj = obj
        self.__dict__.update(adapted_methods)

    def __getattr__(self, attr):
        return getattr(self.obj, attr)

    def original_dict(self):
        return self.obj.__dict__
    
