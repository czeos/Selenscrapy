import logging
import shutil
import toml
from fastapi import APIRouter, HTTPException
from filelock import FileLock

from config import setting, CONFIG_PATH
from db import Neo4jClient
from vkontakte.api_schema import VkUserRequest, VkCredentialsResponse
from vkontakte.scrapers import VkClient, VkUserAPI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='vkontakte.log')

vkontakte_router = APIRouter(
    prefix="/vkontakte",
    tags=["vkontakte"],
    responses={404: {"description": "Not found"}},
)

@vkontakte_router.get("/credentials", response_model=VkCredentialsResponse)
async def get_vk_credentials():
    """
    Return actual VK credentials from the config file.
    :return:
    """
    return setting.vkontakte

@vkontakte_router.put("/credentials", response_model=VkCredentialsResponse)
async def update_vk_credentials(credentials: VkCredentialsResponse):
    """
    Update VK credentials in the config file. Url token can be obtained from the website https://vkhost.github.io/
    Login and password can be used to get the token (not implemented yet).
    :param credentials:
    :return:
    """
    temp_config_path = CONFIG_PATH.with_suffix('.tmp')
    lock = FileLock(f"{CONFIG_PATH}.lock")
    try:
        with lock:
            setting.vkontakte = credentials
            with open(temp_config_path, 'w') as file:
                toml.dump(setting.model_dump(), file)
            shutil.move(temp_config_path, CONFIG_PATH)
        return credentials
    except Exception as e:
        if temp_config_path.exists():
            temp_config_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))

@vkontakte_router.post("/user")
async def get_user_profile(user_request: VkUserRequest):
    """
    Method call Vkontakte scraper and scrape user data from VKontakte API. Data will be imported into neo4j database.
    """
    logging.info(f"get_user_profile called with user_request: {user_request}")

    vk_client = VkClient.from_url(setting.vkontakte.AUTH_URL)
    neo_client = Neo4jClient(uri=setting.neo4j.URI,
                             username=setting.neo4j.USERNAME,
                             password=setting.neo4j.PASSWORD,
                             db_name=setting.neo4j.DB_NAME)

    user = VkUserAPI(id=user_request.id, vk_client=vk_client, neo_client=neo_client)

    try:
        logging.info(f"Fetching user info for user ID: {user_request.id}")
        user.get_user_info(fields=user_request.fields) # get user info
    except Exception as e:
        logging.error(f"Get User Profile failed for user ID: {user_request.id} - {str(e)}")
        raise HTTPException(status_code=500, detail=f'Get User Profile failed: {str(e)}')

    if user_request.friends:
        try:
            logging.info(f"Fetching friends for user ID: {user_request.id}")
            user.ger_user_friends()
        except Exception as e:
            logging.error(f"Get User Friends failed for user ID: {user_request.id} - {str(e)}")
            raise HTTPException(status_code=500, detail=f'Get User Friends failed: {str(e)}')

    try:
        logging.info(f"Saving user profile to Neo4j for user ID: {user_request.id}")
        user.save_user_to_neo4j()
    except Exception as e:
        logging.error(f"Save User to Neo4j failed for user ID: {user_request.id} - {str(e)}")
        raise HTTPException(status_code=500, detail=f'Save User to Neo4j failed: {str(e)}')

    logging.info(f"User profile for user ID: {user_request.id} is saved to the database.")
    return {"status": f"User profile id {user_request.id} is saved to the database."}