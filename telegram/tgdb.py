from telegram_base import TelegramBotBase
from telegram_base import Strategy

class TgdbBotSearch(TelegramBotBase, Strategy):
    
        def __init__(self, api_id, api_hash):
            bot_username = "@tgdb_bot"
            super().__init__(session_name = "tgdb_session", api_id = api_id, api_hash = api_hash, bot_username = bot_username)
    
        async def send(self, msg: str):
            return await self.send_command(f"/info {msg}")
