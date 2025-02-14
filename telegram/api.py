from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import io
from scraper import TelegramScraper
from model import TelegramUser
import uvicorn
import configparser


config = configparser.ConfigParser()
config.read('config.ini')

api_id = config['telegram']['api_id']
api_hash = config['telegram']['api_hash']

app = FastAPI()

#TODO: channel info
@app.get("/info/channel/{channel_name}")
async def get_channel_info(channel_name: str):
    try:
        chanel_link = f"https://t.me/{channel_name}"
        telegramScraper = TelegramScraper("scraper_session", api_id, api_hash)
        tg_channel = await telegramScraper.channel_info(chanel_link)
        
        return tg_channel
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

#TODO: user info
@app.get("/info/user/{username}")
async def get_user_info(username: str):
    telegramScraper = TelegramScraper("scraper_session", api_id, api_hash)
    tg_user = await telegramScraper.scrape_user(username)

    return tg_user

#TODO: scrape channel, csv
@app.get("/channel/{channel_name}")
async def scrape_channel(channel_name: str,csv: bool = False):

    chanel_link = f"https://t.me/{channel_name}"
    telegramScraper = TelegramScraper("scraper_session", api_id, api_hash)

    if csv:
        csv_content = await telegramScraper.scrape_channel_csv(channel=chanel_link)
        response = StreamingResponse(io.StringIO(csv_content), media_type="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename={channel_name}.csv"

        return response
    
    else:
        tg_channel = await telegramScraper.scrape_channel(channel=chanel_link, offset_id=0)
        return tg_channel


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)