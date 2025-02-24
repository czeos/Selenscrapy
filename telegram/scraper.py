import io
from telethon import TelegramClient, functions
import sys
import asyncio
from telethon.tl.types import ChannelParticipantsSearch
import aiohttp
from telethon.errors import RPCError
from model import TelegramMessage, TelegramUser, TelegramChannel, Photo
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetParticipantsRequest,GetFullChannelRequest
import logging
import base64
from telethon.tl import types
import re
import pandas as pd
import json


LOG_FILE = 'scraper.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

class TelegramScraper():


    def __init__(self, session_name:str, api_id: int, api_hash:str):
        self.session_name = session_name
        self.api_id = api_id    
        self.api_hash = api_hash

        self.client = TelegramClient(session_name, api_id, api_hash)

    def is_valid_phone_number(self, phone_number: str) -> bool:

        phone_pattern = re.compile(r"^\+?[1-9]\d{1,14}$")
        return bool(phone_pattern.match(phone_number))

    def get_human_readable_user_status(self,status):
        match status:
            case types.UserStatusOnline():
                return "Currently online"
            case types.UserStatusOffline():
                return status.was_online.strftime("%Y-%m-%d %H:%M:%S %Z")
            case types.UserStatusRecently():
                return "Last seen recently"
            case types.UserStatusLastWeek():
                return "Last seen last week"
            case types.UserStatusLastMonth():
                return "Last seen last month"
            case _:
                return "Unknown"

    def get_entity_type(self,type):
        match type:
            case types.Chat:
                return "Group"
            case types.Channel:
                return "Channel"
            case types.User:
                return "User"
            case types.Message:
                return "Message"
            case _:
                return "Unknown"

    def create_telegram_user(self, user) -> TelegramUser:
            return TelegramUser(
                id=user.id,
                username=user.username,
                user_hash=getattr(user, 'access_hash', None),
                firstname=getattr(user, 'first_name', None),
                lastname=getattr(user, 'last_name', None),
                phone=getattr(user, 'phone', None),
                bot=getattr(user, 'bot', None),
                user_was_online=self.get_human_readable_user_status(user.status) if hasattr(user, 'status') else None
                )

    def create_telegram_channel(self, full_channel, entity) -> TelegramChannel:
        return TelegramChannel(id=full_channel.full_chat.id,
                                         title=entity.title,
                                         name=entity.username,
                                         participants_count=full_channel.full_chat.participants_count if hasattr(full_channel.full_chat, 'participants_count') else None,
                                         description=full_channel.full_chat.about if hasattr(full_channel.full_chat, 'about') else None,
                                         type = self.get_entity_type(type(entity)))

    def remove_duplicates(self, items):
        seen_ids = set()
        unique_list = []
        for item in items:
            if item.id not in seen_ids:
                unique_list.append(item)
                seen_ids.add(item.id)
        
        return unique_list
          
    async def start_client(self):
        if not self.client.is_connected():
            await self.client.start()

    async def close_client(self):
        if self.client.is_connected():
            await self.client.disconnect()

    async def download_media(self, message):
        
        MAX_RETRIES = 5
        if not message.media:
            return None

        try:
            media_file_name = message.file.name if hasattr(message.file, 'name') and message.file.name else f"{message.id}.{message.file.ext}"

            logging.info(f"Downloading {media_file_name}")
            retries = 0
            while retries < MAX_RETRIES:
                try:
                    file_bytes = await message.download_media(file=bytes)       
                    if file_bytes:
                        break
                except (TimeoutError, aiohttp.ClientError, RPCError) as e:
                    retries += 1
                    logging.warning(f"Retrying download for message {message.id}. Attempt {retries}...")
                    await asyncio.sleep(2 ** retries)

        except Exception as e:
            logging.error(f"Error downloading media for message {message.id}: {e}")

        return file_bytes,media_file_name

    async def download_profile_photos(self, user):
        list_of_photos = [] 
        photos = await self.client.get_profile_photos(user)
        for idx, photo in enumerate(photos, start=1):
            photo_media = await self.client.download_media(photo, file=bytes)
            photo_data = base64.b64encode(photo_media).decode('utf-8')
            list_of_photos.append(Photo(date=photo.date, data=photo_data))

        return list_of_photos

    async def get_users_from_channel(self, channel):
        try:
            users = []
            participants = await self.client(GetParticipantsRequest(channel, ChannelParticipantsSearch(''), 0, 100,hash=0))
            return participants.users
        
        except Exception as e:
            logging.error(f'Failed to get users from the channel {channel}: {e}')

    async def scrape_channel(self,channel, limit=100,offset_id=0):
        
        await self.start_client()
        try:
            entity = await self.client.get_entity(channel)
            full_channel = await self.client(GetFullChannelRequest(entity))
            tg_channel = self.create_telegram_channel(full_channel, entity)

            total_messages = 0
            processed_messages = 0

            async for message in self.client.iter_messages(entity, offset_id=offset_id, reverse=True,limit=limit):
                total_messages += 1

            if total_messages == 0:
                logging.info(f"No messages found in channel {channel}.")
                return
            
            users = []
            processed_messages = 0
            async for message in self.client.iter_messages(entity, offset_id=offset_id, reverse=True,limit=limit):
                try:
                    sender = await message.get_sender()
                    tg_msg = TelegramMessage(id=message.id,
                                                sender_id=message.sender_id,
                                                date=message.date,
                                                reply_to_msg_id=message.reply_to_msg_id,
                                                views=message.views,
                                                content=message.text,
                                                type = self.get_entity_type(type(message)))

                    if message.forward:  
                        fwd_from = await self.check_telegram_entity(id = message.forward.from_id.channel_id)
                        tg_msg.forward_from = fwd_from.name

                    if sender:
                        tg_user = self.create_telegram_user(sender)
                        users.append(sender)
                        tg_msg.sender = tg_user
                    
                    tg_channel.messages.append(tg_msg)

                    #if message.replies:
                    #    tg_msg.replies.append(message.replies)

                    if message.media and False:
                        media_bytes,file_name = await self.download_media(message)
                        tg_msg.data = media_bytes
                        tg_msg.file_name = file_name

                    processed_messages += 1

                    progress = (processed_messages / total_messages) * 100
                    logging.info(f"\rScraping channel: {channel} - Progress: {progress:.2f}%")

                except Exception as e:
                    logging.error(f"Error processing message {message.id}: {e}")
            try:
                all_users = await self.get_users_from_channel(entity)
                users.extend(all_users)

            except Exception as e:
                logging.error(f"Error fetching users from channel {channel}: {e}")

            users = self.remove_duplicates(users)

            for user in users:
                tg_user = self.create_telegram_user(user)
                tg_user.photos = await self.download_profile_photos(user)
                tg_channel.users.append(tg_user)

            return tg_channel
        except Exception as e:
            logging.error(e)

    async def scrape_channel_csv(self,channel, offset_id=0, exclude_fields=None):
        if exclude_fields is None:
            exclude_fields = []

        tg_channel = await self.scrape_channel(channel = channel,offset_id=offset_id)
      
        if not tg_channel or not tg_channel.messages:
            return

        messages_json = json.dumps([message.dict() for message in tg_channel.messages], default=str)
        df = pd.json_normalize(json.loads(messages_json))   
        df.drop(columns=exclude_fields, inplace=True, errors='ignore')

        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        return output.getvalue()

    async def check_telegram_phone(self, phone_number):
        await self.start_client()
        try:
            contact = types.InputPhoneContact(
                client_id=0, phone=phone_number, first_name="", last_name=""
            ) 
            contacts = await self.client(functions.contacts.ImportContactsRequest([contact]))            
            
            users = contacts.to_dict().get("users", [])
            number_of_matches = len(users)

            if number_of_matches == 1:
                updates_response: types.Updates = await self.client(functions.contacts.DeleteContactsRequest(id=[users[0].get("id")]))
                user = updates_response.users[0]

                tg_user = self.create_telegram_user(user)

                return tg_user
            else:
                return None  

        except Exception as e:
            logging.error(f"Failed to check Telegram account for phone number {phone_number}: {e}")

    async def check_telegram_entity(self, username = None, id = None):
        try:
            await self.start_client()
            if id is not None:
                input = await self.client.get_entity(id)
            else:
                input = await self.client.get_entity(username)

            if isinstance(input, types.User):
                full_user = await self.client(GetFullUserRequest(input))

                users = full_user.to_dict().get("users", [])
                number_of_matches = len(users)

                if number_of_matches == 1:
                    user = full_user.users[0]
                    
                    tg_user = self.create_telegram_user(user)
                    tg_user.photos = await self.download_profile_photos(user)

                tg_user.type = "User"
                return tg_user

            elif isinstance(input, types.Channel):

                full_channel = await self.client(GetFullChannelRequest(input))
                tg_channel = self.create_telegram_channel(full_channel, input) 

                return tg_channel

            elif isinstance(input, types.Chat):

                full_channel = await self.client(GetFullChannelRequest(input))
                tg_channel = self.create_telegram_channel(full_channel, input) 
                return tg_channel

        except Exception as e:
            logging.error(f"An error occurred while fetching user info: {e}")

