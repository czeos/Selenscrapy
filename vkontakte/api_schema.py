from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict, AliasChoices

from vkontakte.vk_api_schema import VkUserRequestSchema


class VkCredentialsResponse(BaseModel):
    API_VERSION: str
    AUTH_URL: str
    LOGIN: str
    PWD: str
    ACCESS_TOKEN: str


class VkUserApiRequest(BaseModel):
    request: VkUserRequestSchema
    friends: bool = Field(default=True, description="If True, the user's friends will be scraped. Default is True.")
    model_config = ConfigDict(json_schema_extra={
            "examples": [
                {"request": {"id": 896119729, "fields": ["first_name", "last_name", "city", "country"]},
                 "friends": True}

            ]
        }
    )


class VkWallApiRequest(BaseModel):
    id: int = Field(..., description="Owner ID (integer)", validation_alias=AliasChoices("id", "uid"))
    domain: Optional[str] = Field(default=None, description="Domain name of the user's wall. If None, the user's wall ")


    fields: Optional[List[str]] = Field(default=None, description="OPTIONAL: Specify which fields will be put to VK "
                                                                  "API method 'users.get'. Description here: "
                                                                  "https://dev.vk.com/en/reference/objects/user. "
                                                                  "If None, all fields will be returned.")
    friends: bool = Field(default=True, description="If True, the user's friends will be scraped. Default is True.")

    model_config = ConfigDict(json_schema_extra={
            "examples": [
                {
                    "id": 896119729,
                    "filed": ["first_name", "last_name", "city", "country"],
                    "friends": True,
                }
            ]
        }
    )

class ScreenNameResolveApiRequest(BaseModel):
    screen_name: Optional[str] = Field(default='', description="VKontakte Screen Name (string), can be name or url")
