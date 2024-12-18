from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class VkCredentialsResponse(BaseModel):
    API_VERSION: str
    AUTH_URL: str
    LOGIN: str
    PWD: str


class VkUserRequest(BaseModel):
    id: int = Field(..., description="User ID (integer)")
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