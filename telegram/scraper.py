from telethon import TelegramClient
import sys
import asyncio
import io
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, User, PeerChannel,ChannelParticipantsSearch
import aiohttp
from telethon.errors import RPCError
from model import TelegramMessage, TelegramUser, TelegramChannel, Photo
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetParticipantsRequest
import csv
import logging
import base64


# Configure logging
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
    
    def create_telegram_user(self, user) -> TelegramUser:
            return TelegramUser(
                id=user.id,
                username=user.username,
                user_hash=user.access_hash,
                firstname=getattr(user, 'first_name', None),
                lastname=getattr(user, 'last_name', None),
                phone=getattr(user, 'phone', None),
                bot=getattr(user, 'bot', None))

    def remove_duplicates(self, items):
        #TODO: Jak nechat jen jednoho usera ale toho ktery ma profilovku
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
            for user in participants.users: 
                tg_user = self.create_telegram_user(user)       
                users.append(tg_user)
                
            return users
        except Exception as e:
            logging.error(f'Failed to get users from the channel {channel}: {e}')

    async def channel_info(self, channel_name = None, channel_id = None):
        await self.start_client()
        try:
            if channel_id:
                entity = await self.client.get_entity(PeerChannel(channel_id))
            else:
                entity = await self.client.get_entity(channel_name)

        except Exception as e:
            logging.error(f"Failed to get entity for channel {channel_name}: {e}")
            return None
        return {
            "id": entity.id,
            "title": entity.title,
            "username": entity.username,
            "participants_count": entity.participants_count if hasattr(entity, 'participants_count') else None,
            "description": entity.about if hasattr(entity, 'about') else None
        }

    async def scrape_channel(self,channel, limit=100,offset_id=0):
        
        await self.start_client()
        try:
            entity = await self.client.get_entity(channel)
            tg_channel = TelegramChannel(id=entity.id)

            total_messages = 0
            processed_messages = 0

            async for message in self.client.iter_messages(entity, offset_id=offset_id, reverse=False,limit=limit):
                total_messages += 1

            if total_messages == 0:
                logging.info(f"No messages found in channel {channel}.")
                return
            
            users = []
            processed_messages = 0
            async for message in self.client.iter_messages(entity, offset_id=offset_id, reverse=False,limit=limit):
                try:
                    sender = await message.get_sender()
                    tg_msg = TelegramMessage(id=message.id,
                                                sender_id=message.sender_id,
                                                date=message.date,
                                                reply_to_msg_id=message.reply_to_msg_id,
                                                views=message.views,
                                                content=message.text
                                                )

                    if message.forward:  
                        fwd_from = await self.channel_info(channel_id = message.forward.from_id.channel_id)
                        tg_msg.forward = fwd_from["username"]

                    if sender:
                        tg_user = self.create_telegram_user(sender)
                        users.append(sender)
                        tg_msg.sender = tg_user
                    
                    tg_channel.messages.append(tg_msg)

                    #if message.replies:
                    #    tg_msg.replies.append(message.replies)

                    if message.media:
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

    async def scrape_channel_csv(self,channel, exclude_fields=None):
        if exclude_fields is None:
            exclude_fields = []

        exclude_fields.extend(['data', 'replies'])

        tg_channel = await self.scrape_channel(channel = channel)

        if not tg_channel or not tg_channel.messages:
            return

        fields = [field for field in tg_channel.messages[0].__dict__.keys() if field not in exclude_fields]
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(fields)
        
        for msg in tg_channel.messages:
            row = [getattr(msg, field) for field in fields]
            writer.writerow(row)

        return output.getvalue()

    async def scrape_user(self, username):
        try:
            await self.start_client()
            inputUser = await self.client.get_entity(username)
            full_user = await self.client(GetFullUserRequest(inputUser))

            users = full_user.to_dict().get("users", [])
            number_of_matches = len(users)

            if number_of_matches == 1:
                user = full_user.users[0]
                
                tg_user = self.create_telegram_user(user)
                
                #user.about, user.status
                tg_user.photos = await self.download_profile_photos(user)
                
            return tg_user  
        except Exception as e:
            logging.error(f"An error occurred while fetching user info: {e}")