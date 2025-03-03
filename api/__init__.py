
from fastapi import FastAPI, HTTPException

from api.logger import api_logger
from api.utils import StatusCodeMsg
from api.schema import APOCTest
from config import Config, CONFIG_PATH
from db import Neo4jClient
from vkontakte.api import vkontakte_router
from vkontakte.api_schema import VkUserApiRequest

app = FastAPI()
app.include_router(vkontakte_router)

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint to check if the server is running.
    """
    return {"detail": "Server is runing."}

healthy = StatusCodeMsg(status_code=200, description='Service is healthy', message='connected')
not_connected = StatusCodeMsg(status_code=503, description='Service is unavailable',
                              message="Unable to connect to the database. Check logs for details." )
@app.get("/db/health", tags=["Database"], responses={
    200: healthy.model_dump(),
    503: not_connected.model_dump()})
def database_health_check():
    """
    Endpoint to check the health of the Neo4j database connection.
    """
    config = Config(config_path=CONFIG_PATH)

    client = Neo4jClient(uri=config.neo4j.URI,
                         username=config.neo4j.USERNAME,
                         password=config.neo4j.PASSWORD,
                         db_name=config.neo4j.DB_NAME)

    if client.health_check():
        return healthy.get_status_msg()
    else:
        raise HTTPException(status_code=503,detail=not_connected.message)


@app.get("/{id}", tags=["APOC"])
async def apoc_load_Json_query_path(id: int):
    """
    Endpoint to check if APOC is working and sending data to external services with parameters in the url path.
    """
    return {"detail": f"returning value: {id}"}


@app.post("/jsonParams", tags=["APOC"])
async def apoc_load_JsonParam_query_path(params: VkUserApiRequest):
    """
    Endpoint to check if APOC is working and sending POST data to external services with parameters in the url path.

    Testing with the following schema VkUserRequest:
    """
    # Log the input parameters
    api_logger.debug(f"Received params: {params.model_dump()}")

    return {"detail": f"returning value: {params.model_dump()}"}