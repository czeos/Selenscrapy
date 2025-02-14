from telethon import TelegramClient, events
import asyncio


class TelegramBotBase():

    def __init__(self, session_name:str, api_id: int, api_hash:str, bot_username: str):

        self.session_name = session_name
        self.api_id = api_id    
        self.api_hash = api_hash
        self.bot_username = bot_username    

        self.client = TelegramClient(session_name, api_id, api_hash)


    async def start_client(self):

        if not self.client.is_connected():
            await self.client.start()
    
    def send_command_sync(self,arg:str) -> str:
        response = asyncio.run(self.send_command(arg))
        return response
        
    async def send_command(self, msg: str) -> str:

        await self.start_client()
        await self.client.send_message(self.bot_username, msg)
        response = await self._listen_for_reply()
        return response

    async def _listen_for_reply(self):
        future = asyncio.Future()

        @self.client.on(events.NewMessage(from_users=self.bot_username))
        async def _handler(event):
            if not future.done():
                future.set_result(event.text)
                self.client.remove_event_handler(_handler)

        return await future
