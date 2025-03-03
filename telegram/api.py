from tgdb import TgdbBotSearch
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import io
import uvicorn
from telegram_base import BotContext
from scraper import TelegramScraper
from config import Config


config = Config()
api_id = config.get('telegram', 'api_id')
api_hash = config.get('telegram', 'api_hash')

app = FastAPI()

@app.get("/info/entity/{param}")
async def get_user_info(param: str):
    try:
        telegramScraper = TelegramScraper("scraper_session", api_id, api_hash)
        if telegramScraper.is_valid_phone_number(param):
            tg_user = await telegramScraper.check_telegram_phone(param)
        else:
            tg_user = await telegramScraper.check_telegram_entity(username=param)
    finally:
        await telegramScraper.close_client()
    
    return tg_user

@app.get("/channel/{channel_name}")
async def scrape_channel(channel_name: str,csv: bool = False, offset_id: int = 0):

    chanel_link = f"https://t.me/{channel_name}"
    telegramScraper = TelegramScraper("scraper_session", api_id, api_hash)
    try:
        if csv:
            csv_content = await telegramScraper.scrape_channel_csv(channel=chanel_link, offset_id=offset_id, exclude_fields = ['data', 'replies','sender','sender.photos'])
            response = StreamingResponse(io.StringIO(csv_content), media_type="text/csv")
            response.headers["Content-Disposition"] = f"attachment; filename={channel_name}.csv"

            return response

        else:
            tg_channel = await telegramScraper.scrape_channel(channel=chanel_link, offset_id=offset_id)
            return tg_channel
    finally:
        await telegramScraper.close_client()

@app.get("/bot/{param}")
async def info(param: str):
    
    tgdbBotSearch  = TgdbBotSearch(api_id, api_hash)
    context = BotContext(tgdbBotSearch)
    result = await context.work(param)

    return { "response": result}    

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)