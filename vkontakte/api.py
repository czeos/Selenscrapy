import logging
from fastapi import APIRouter, HTTPException

from config import setting
from db import Neo4jClient
from vkontakte.api_schema import VkUserRequest, VkCredentialsResponse, ScreenNameResolveRequest
from vkontakte.scrapers import VkClient, VkUserAPI, ScreeNameAPI, vk_client
from vkontakte.utils import update_vk_credentials

vkontakte_router = APIRouter(
    prefix="/vkontakte",
    tags=["vkontakte"],
    responses={404: {"description": "Not found"}},
)

@vkontakte_router.get("/credentials", response_model=VkCredentialsResponse)
def get_vk_credentials():
    """
    Return actual VK credentials from the config file.
    :return:
    """
    return setting.vkontakte

@vkontakte_router.put("/credentials", response_model=VkCredentialsResponse)
def update_vk_credentials(credentials: VkCredentialsResponse):
    """
    Update VK credentials in the config file. Url token can be obtained from the website https://vkhost.github.io/
    Login and password can be used to get the token (not implemented yet).
    :param credentials:
    :return:
    """
    try:
        return update_vk_credentials(credentials)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@vkontakte_router.post("/user")
def get_user_profile(user_request: VkUserRequest):
    """
    Method call Vkontakte scraper and scrape user data from VKontakte API. Data will be imported into neo4j database.
    Method will return the status of the operation as JSON. All status messages codes are 200, because problems with error handling on the side of no4j apoc
    """
    logging.info(f"get_user_profile called with user_request: {user_request}")

    neo_client = Neo4jClient(uri=setting.neo4j.URI,
                             username=setting.neo4j.USERNAME,
                             password=setting.neo4j.PASSWORD,
                             db_name=setting.neo4j.DB_NAME)

    user = VkUserAPI(id=user_request.id, vk_client=vk_client, neo_client=neo_client)

    try:
        logging.info(f"Fetching VkUser info for user ID: {user_request.id}")
        user.get_user_info(fields=user_request.fields) # get user info
    except Exception as e:
        logging.error(f"Get VkUser Profile failed for user ID: {user_request.id} - {str(e)}")
        # raise HTTPException(status_code=500, detail=f'Get User Profile failed: {str(e)}')
        return {"code": 500, "detail": f"Get User Profile failed for user ID: {user_request.id} - {str(e)}"}

    try:
        logging.info(f"Saving VkUser into noe4J: {user_request.id}")
        user_node = user.save_user_to_neo4j() # save user to neo4j
    except Exception as e:
        logging.error(f"Save User to Neo4j failed for user ID: {user_request.id} - {str(e)}")
        return {"code": 500, "detail": f"Save User to Neo4j failed for user ID: {user_request.id} - {str(e)}"}
        # raise HTTPException(status_code=500, detail=f'Save User to Neo4j failed: {str(e)}')

    if user_request.friends:
        try:
            logging.info(f"Fetching friends for user ID: {user_request.id}")
            user.ger_user_friends()
        except Exception as e:
            logging.error(f"Get User Friends failed for user ID: {user_request.id} - {str(e)}")
            return {"code": 500, "detail": f"Get User Friends failed for user ID: {user_request.id} - {str(e)}"}
            # raise HTTPException(status_code=500, detail=f'Get User Friends failed: {str(e)}')

        try:
            logging.info(f"Saving friends for user ID: {user_request.id}")
            user.save_user_friends_to_neo4j(user_node)
        except Exception as e:
            logging.error(f"Save Friends to Neo4j failed for user ID: {user_request.id} - {str(e)}")
            return {"code": 500, "detail": f"Save Friends to Neo4j failed for user ID: {user_request.id} - {str(e)}"}
            # raise HTTPException(status_code=500, detail=f'Save Friends to Neo4j failed: {str(e)}')

    logging.info(f"User profile for user ID: {user_request.id} is saved to the database.")
    return {"code": 200, "detail": f"User profile id {user_request.id} is saved to the database."}

@vkontakte_router.post("/wall")
def get_wall(user_request: VkUserRequest):
    """
    Method call Vkontakte scraper and scrape user data from VKontakte API. Data will be imported into neo4j database.
    Method will return the status of the operation as JSON. All status messages codes are 200, because problems with error handling on the side of no4j apoc
    """
    logging.info(f"get_user_profile called with user_request: {user_request}")

    neo_client = Neo4jClient(uri=setting.neo4j.URI,
                             username=setting.neo4j.USERNAME,
                             password=setting.neo4j.PASSWORD,
                             db_name=setting.neo4j.DB_NAME)

    user = VkUserAPI(id=user_request.id, vk_client=vk_client, neo_client=neo_client)

    try:
        logging.info(f"Fetching VkUser info for user ID: {user_request.id}")
        user.get_user_info(fields=user_request.fields) # get user info
    except Exception as e:
        logging.error(f"Get VkUser Profile failed for user ID: {user_request.id} - {str(e)}")
        # raise HTTPException(status_code=500, detail=f'Get User Profile failed: {str(e)}')
        return {"code": 500, "detail": f"Get User Profile failed for user ID: {user_request.id} - {str(e)}"}

    try:
        logging.info(f"Saving VkUser into noe4J: {user_request.id}")
        user_node = user.save_user_to_neo4j() # save user to neo4j
    except Exception as e:
        logging.error(f"Save User to Neo4j failed for user ID: {user_request.id} - {str(e)}")
        return {"code": 500, "detail": f"Save User to Neo4j failed for user ID: {user_request.id} - {str(e)}"}
        # raise HTTPException(status_code=500, detail=f'Save User to Neo4j failed: {str(e)}')

    if user_request.friends:
        try:
            logging.info(f"Fetching friends for user ID: {user_request.id}")
            user.ger_user_friends()
        except Exception as e:
            logging.error(f"Get User Friends failed for user ID: {user_request.id} - {str(e)}")
            return {"code": 500, "detail": f"Get User Friends failed for user ID: {user_request.id} - {str(e)}"}
            # raise HTTPException(status_code=500, detail=f'Get User Friends failed: {str(e)}')

        try:
            logging.info(f"Saving friends for user ID: {user_request.id}")
            user.save_user_friends_to_neo4j(user_node)
        except Exception as e:
            logging.error(f"Save Friends to Neo4j failed for user ID: {user_request.id} - {str(e)}")
            return {"code": 500, "detail": f"Save Friends to Neo4j failed for user ID: {user_request.id} - {str(e)}"}
            # raise HTTPException(status_code=500, detail=f'Save Friends to Neo4j failed: {str(e)}')

    logging.info(f"User profile for user ID: {user_request.id} is saved to the database.")
    return {"code": 200, "detail": f"User profile id {user_request.id} is saved to the database."}

@vkontakte_router.post("/resolve")
def resolve_screen_name(request: ScreenNameResolveRequest):
    resolve = ScreeNameAPI(vk_client=vk_client)
    if request.screen_name:
        try:
            response = resolve.resolve_screen_name(request.screen_name)
            return response.model_dump()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    elif request.url:
        screen_name = resolve.strip_url(request.url)
        try:
            response = resolve.resolve_screen_name(screen_name)
            return response.model_dump()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Either screen_name or url must be provided.")
