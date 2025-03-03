from datetime import datetime
from pydantic import BaseModel, Field, AliasChoices, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from functools import partial
from db.model import VkUserNode, CityNode, CountryNode


class BaseModelConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra='ignore')

# mapping of Vkontatke integer values to boolean and string values
int2bool = {1: True, 0: False}

realionst2str = {0: "Not specified",
                 1: "not married",
                 2: "in a relationship",
                 3: "engaged",
                 4: "married",
                 5: "complicated",
                 6: "actively searching",
                 7: "in love",
                 8: "in a civil union"}

sex2str = {0: "not specified", 1: "female", 2: "male"}

def int_mapping(value, map):
    """"""
    return map[value]

vk_int2bool = partial(int_mapping, map=int2bool)
vk_realation2str = partial(int_mapping, map=realionst2str)
vk_sex2str = partial(int_mapping, map=sex2str)

# Pydantic models
class VkScreenNameResolveRequestSchema(BaseModelConfig):
    screen_name: str = Field(..., description="Screen name to resolve.")

    @field_validator("screen_name", mode='before')
    @classmethod
    def strip_url(cls, data: str) -> str:
        if data.__contains__('vk.com/'):
            return data.split('vk.com/')[1]
        return data

class VkScreenNameResolveResponse(BaseModelConfig):
    """
    Response model for the Vkontakte screen name resolve
    attributes:
    - object_id: int - Object ID (integer)
    - type: str - Object type (string)
    - screen_name: Optional[str] - Screen name (string)
    """
    screen_name: Optional[str] = Field(default='', description="Screen name (string)")
    object_id: int = Field(..., description="Object ID (integer)")
    type: str = Field(..., description="Object type (string)")

class VkCountrySchema(BaseModelConfig):
    id: int = Field(..., description="Vk country ID (integer)",
                    serialization_alias="vk_id",
                    validation_alias=AliasChoices('id','vk_id'))
    name: str = Field(..., description="Country title (string)", validation_alias=AliasChoices('name', 'title'))

    class Meta:
        node = CountryNode

class VkCitySchema(BaseModelConfig):
    id: int = Field(..., description="Vk city ID (integer)",
                    serialization_alias="vk_id",
                    validation_alias=AliasChoices('id','vk_id'))
    name: str = Field(..., description="Country title (string)", validation_alias=AliasChoices('name', 'title'))

    class Meta:
        node = CityNode


class VkUserRequestSchema(BaseModelConfig):
    user_ids: int = Field(..., description="Vk user ID (integer), comma-separated list of IDs",
                    serialization_alias="vk_id",
                    validation_alias=AliasChoices('user_ids', 'vk_id', 'id'))
    fields: Optional[List[str]] = Field(None, description="OPTIONAL: Specify which fields will be put to VK "
                                                          "API method 'users.get'. Description here: "
                                                          "https://dev.vk.com/en/reference/objects/user. "
                                                          "If None, all fields will be returned.")
    from_group: Optional[int] = Field(None, description="Whether the user is from a group.")



class VkUserResponseSchema(BaseModelConfig):
    id: int = Field(..., description="User ID (integer)",
                    serialization_alias="vk_id",
                    validation_alias=AliasChoices('id','vk_id'))
    first_name: str = Field(..., description="User's first name (string)")
    last_name: str = Field(..., description="User's last name (string)")
    deactivated: Optional[str] = Field(None, description="Account status: 'deleted' or 'banned' (string)")
    hidden: Optional[bool] = Field(None, description="Whether the user is hidden (1 if hidden, integer)")
    about: Optional[str] = Field(None, description="About me section (string)")
    activities: Optional[str] = Field(None, description="Activities section (string)")
    bdate: Optional[str] = Field(None, description="Birthdate in ISO format parsed from DD.MM.YYYY format (string)")
    blacklisted: Optional[bool] = Field(None, description="Whether the user is blacklisted by the current user.(1 or 0, integer) to bool")
    books: Optional[str] = Field(None, description="Favorite books section (string)")
    can_access_closed: Optional[bool] = Field(None, description="Whether the user can access their private data (1 or 0, integer)")
    can_post: Optional[int] = Field(None, description="Whether the user can post on their wall (1 or 0, integer)")
    can_see_all_posts: Optional[bool] = Field(None, description="Whether the user can see all posts (1 or 0, integer)")
    can_see_audio: Optional[bool] = Field(None, description="Whether the user can see audio recordings (1 or 0, integer)")
    can_send_friend_request: Optional[int] = Field(None, description="Whether the user can send a friend request (1 or 0, integer)")
    can_write_private_message: Optional[int] = Field(None, description="Whether the user can send private messages (1 or 0, integer)")
    career: Optional[List[Dict[str, Any]]] = Field(None, description="Career information (array of objects)")
    city: Optional[VkCitySchema] = Field(None, description="City information (object with id and title)")
    common_count: Optional[int] = Field(None, description="Number of mutual friends (integer)")
    connections: Optional[Dict[str, Any]] = Field(None, description="External social network accounts (object)")
    contacts: Optional[Dict[str, Any]] = Field(None, description="User's contact information (object)")
    counters: Optional[Dict[str, Any]] = Field(None, description="User's counters (object with fields like friends, photos, etc.)")
    country: Optional[VkCountrySchema] = Field(None, description="Country information (object with id and title)")
    crop_photo: Optional[Dict[str, Any]] = Field(None, description="Cropped photo information (object)")
    domain: Optional[str] = Field(None, description="User's short domain (string)")
    education: Optional[Dict[str, Any]] = Field(None, description="Education information (object)")
    exports: Optional[Dict[str, Any]] = Field(None, description="Exported services (object)")
    followers_count: Optional[int] = Field(None, description="Number of followers (integer)")
    friend_status: Optional[int] = Field(None, description="Friendship status (integer, 0-3)")
    games: Optional[str] = Field(None, description="Favorite games section (string)")
    has_mobile: Optional[bool] = Field(None, description="Whether the user has a mobile number (1 or 0, integer)")
    has_photo: Optional[bool] = Field(None, description="Whether the user has a profile photo (1 or 0, integer)")
    home_town: Optional[str] = Field(None, description="User's hometown (string)")
    interests: Optional[str] = Field(None, description="User's interests (string)")
    is_closed: Optional[bool] = Field(None, description="Whether the user's profile is hidden by privacy settings (boolean)")
    is_favorite: Optional[int] = Field(None, description="Whether the user is marked as a favorite (1 or 0, integer)")
    is_friend: Optional[int] = Field(None, description="Whether the user is a friend (1 or 0, integer)")
    is_hidden_from_feed: Optional[bool] = Field(None, description="Whether the user is hidden from feed (1 or 0, integer)")
    last_seen: Optional[Dict[str, Any]] = Field(None, description="Last seen information (object with time and platform)")
    lists: Optional[List[int]] = Field(None, description="List IDs where the user is included (array of integers)")
    maiden_name: Optional[str] = Field(None, description="User's maiden name (string)")
    military: Optional[List[Dict[str, Any]]] = Field(None, description="Military service information (array of objects)")
    movies: Optional[str] = Field(None, description="Favorite movies section (string)")
    music: Optional[str] = Field(None, description="Favorite music section (string)")
    nickname: Optional[str] = Field(None, description="User's nickname (string)")
    occupation: Optional[Dict[str, Any]] = Field(None, description="Occupation information (object)")
    online: Optional[int] = Field(None, description="Whether the user is online (1 or 0, integer)")
    personal: Optional[Dict[str, Any]] = Field(None, description="Personal information (object)")
    photo_id: Optional[str] = Field(None, description="Photo ID (string)")
    photo_max_orig: Optional[str] = Field(None, description="URL of the maximum original size profile photo (string)")
    quotes: Optional[str] = Field(None, description="Favorite quotes section (string)")
    relation: Optional[str] = Field(None, description="Relationship status (integer, 1-8)")
    relatives: Optional[List[Dict[str, Any]]] = Field(None, description="Relatives information (array of objects)")
    schools: Optional[List[Dict[str, Any]]] = Field(None, description="School information (array of objects)")
    screen_name: Optional[str] = Field(None, description="Screen name (string)")
    sex: Optional[str] = Field(None, description="Gender (1: female, 2: male, 0: unknown, integer)")
    site: Optional[str] = Field(None, description="Website (string)")
    status: Optional[str] = Field(None, description="Status text (string)")
    status_audio: Optional[Dict[str, Any]] = Field(None, description="Audio status information (object)")
    timezone: Optional[int] = Field(None, description="Timezone offset in hours (integer)")
    trending: Optional[int] = Field(None, description="Whether the user is trending (1 or 0, integer)")
    tv: Optional[str] = Field(None, description="Favorite TV shows section (string)")
    universities: Optional[List[Dict[str, Any]]] = Field(None, description="University information (array of objects)")
    verified: Optional[bool] = Field(None, description="Whether the user is verified (1 or 0, integer)")
    wall_comments: Optional[int] = Field(None, description="Whether wall comments are allowed (1 or 0, integer)")

    @field_validator("bdate")
    @classmethod
    def vk_datetime_to_iso(cls, value):
        try:
            # Try parsing full date
            return datetime.strptime(value, "%d.%m.%Y").isoformat()
        except ValueError:
            # Try parsing day and month only
            try:
                return datetime.strptime(value, "%d.%m").isoformat()
            except ValueError:
                return None

    # validations
    blacklisted2bol = field_validator("blacklisted", mode='before')(vk_int2bool)
    can_access_closed2bol = field_validator("can_access_closed", mode='before')(vk_int2bool)
    can_see_audio2bol = field_validator("can_see_audio", mode='before')(vk_int2bool)
    has_mobile2bol = field_validator("has_mobile", mode='before')(vk_int2bool)
    has_photo2bol = field_validator("has_photo", mode='before')(vk_int2bool)
    is_hidden_from_feed2bol = field_validator("is_hidden_from_feed", mode='before')(vk_int2bool)
    relation_int2str = field_validator("relation", mode='before')(vk_realation2str)
    sex_int2str = field_validator('sex', mode='before')(vk_sex2str)
    verified2bol = field_validator("verified", mode='before')(vk_int2bool)
    hidden2bool = field_validator("hidden", mode='before')(vk_int2bool)

    class Meta:
        node = VkUserNode
        # list of the nested nodes
        nested_nodes = ['country', 'city']


class VkUserFriendLis(BaseModelConfig):
    id: int = Field(..., description="Vk friend list ID (integer)",
                    serialization_alias="vk_id",
                    validation_alias=AliasChoices('id','vk_id'))
    name: str = Field(description="User friend list name (string)")

class VkFriendRequestSchema(BaseModelConfig):
    user_id: int = Field(..., description="Vk user ID (integer)",
                    serialization_alias="vk_id",
                    validation_alias=AliasChoices('user_id', 'vk_id', 'id'))
    order: Optional[str] = Field(None, description="Order of the friends list.")
    list_id: Optional[int] = Field(None, description="ID of the friends list.")
    fields: Optional[List[str]] = Field(None, description="List of fields to retrieve.")
    count: Optional[int] = Field(None, description="Number of friends to retrieve.")
    offset: Optional[int] = Field(None, description="Offset for the friends list.")

class VkAddressSchema(BaseModelConfig):
    id: int = Field(..., description="Vk address list ID (integer)",
                    serialization_alias="vk_id",
                    validation_alias=AliasChoices('id', 'vk_id'))
    address: str = Field(..., description="Full address.")
    city: VkCitySchema = Field(..., description="City where the address is located.")
    country: VkCountrySchema = Field(..., description="Country where the address is located.")
    title: str = Field(..., description="Title of the address.")
    work_info_status: str = Field(..., description="Work information status related to the address.")

class VkAddressesSchema(BaseModelConfig):
    is_enabled: bool = Field(..., description="Indicates if addresses are enabled.")
    main_address_id: int = Field(..., description="Unique identifier of the main address.")
    main_address: VkAddressSchema = Field(..., description="Details of the main address.")
    count: int = Field(..., description="Number of addresses available.")

class VkContactSchema(BaseModelConfig):
    id: int = Field(..., description="Vk user contact  ID (integer)",
                    serialization_alias="vk_id",
                    validation_alias=AliasChoices('user_id', 'vk_id', 'id'))

class VkLinkSchema(BaseModelConfig):
    id: int = Field(..., description="Vk link  ID (integer)",
                    serialization_alias="vk_id",
                    validation_alias=AliasChoices('id', 'vk_id'))
    name: str = Field(..., description="Name of the link.")
    desc: str = Field(..., description="Description of the link.")
    photo_100: str = Field(..., description="URL of the 100px photo for the link.")
    url: str = Field(..., description="URL of the link.")

class VkGroupSchema(BaseModelConfig):
    id: int = Field(..., description="Vk group  ID (integer)",
                    serialization_alias="vk_id",
                    validation_alias=AliasChoices('id', 'vk_id'))
    description: Optional[str] = Field(None, description="Description of the group.")
    links: Optional[List[VkLinkSchema]] = Field(None, description="List of related links for the group.")
    contacts: Optional[List[VkContactSchema]] = Field(None, description="List of contacts related to the group.")
    addresses: Optional[VkAddressesSchema] = Field(None, description="Addresses associated with the group.")
    name: Optional[str] = Field(None, description="Name of the group.")
    screen_name: Optional[str] = Field(None, description="Screen name (short name) of the group.")
    is_closed: Optional[int] = Field(None, description="Privacy status of the group (0 - open, 1 - closed, 2 - private).")
    type: Optional[str] = Field(None, description="Type of the group (e.g., group, page, event).")
    is_admin: Optional[int] = Field(None, description="Indicates if the user is an admin (1 - yes, 0 - no).")
    is_member: Optional[int] = Field(None, description="Indicates if the user is a member (1 - yes, 0 - no).")
    is_advertiser: Optional[int] = Field(None, description="Indicates if the user is an advertiser (1 - yes, 0 - no).")
    photo_200: Optional[str] = Field(None, description="URL of the 200px photo for the group.")
    status: Optional[str] = Field(None, description="Status of the group.")
    verified: Optional[int] = Field(None, description="Verification status of the group (1 - verified, 0 - not verified).")
    deactivated: Optional[str] = Field(None, description="Deactivation reason, if applicable.")
    members_count: Optional[int] = Field(None, description="Number of members in the group.")
    activity: Optional[str] = Field(None, description="Activity status of the group.")
    age_limits: Optional[int] = Field(None, description="Age restrictions for the group.")
    ban_info: Optional[dict] = Field(None, description="Information about bans in the group.")
    can_create_topic: Optional[bool] = Field(None, description="Indicates if the user can create topics in the group.")
    can_message: Optional[bool] = Field(None, description="Indicates if the user can message the group.")
    can_post: Optional[bool] = Field(None, description="Indicates if the user can post in the group.")
    can_see_all_posts: Optional[bool] = Field(None, description="Indicates if the user can see all posts in the group.")
    can_upload_doc: Optional[bool] = Field(None, description="Indicates if the user can upload documents to the group.")
    can_upload_video: Optional[bool] = Field(None, description="Indicates if the user can upload videos to the group.")
    city: Optional[VkCitySchema] = Field(None, description="City associated with the group.")
    country: Optional[VkCountrySchema] = Field(None, description="Country associated with the group.")
    cover: Optional[dict] = Field(None, description="Cover image information for the group.")
    crop_photo: Optional[dict] = Field(None, description="Crop photo information for the group.")
    fixed_post: Optional[int] = Field(None, description="Identifier of the fixed post in the group.")
    has_photo: Optional[bool] = Field(None, description="Indicates if the group has a photo.")
    is_favorite: Optional[bool] = Field(None, description="Indicates if the group is marked as a favorite.")
    is_hidden_from_feed: Optional[bool] = Field(None, description="Indicates if the group is hidden from the feed.")
    main_album_id: Optional[int] = Field(None, description="Identifier of the main album of the group.")
    main_section: Optional[int] = Field(None, description="Main section of the group.")
    market: Optional[dict] = Field(None, description="Market-related information for the group.")
    member_status: Optional[int] = Field(None, description="Membership status of the user in the group.")
    site: Optional[str] = Field(None, description="Website associated with the group.")
    start_date: Optional[str] = Field(None, description="Start date of the group or event.")
    finish_date: Optional[str] = Field(None, description="Finish date of the group or event.")
    trending: Optional[bool] = Field(None, description="Indicates if the group is trending.")

class VkGroupResponseSchema(BaseModelConfig):
    groups: List[VkGroupSchema] = Field(..., description="List of groups in the response.")
    # profiles: List = Field(..., description="List of profiles in the response.")


class VkSizeSchema(BaseModelConfig):
    height: int = Field(..., description="Height of the image.")
    type: str = Field(..., description="Type of the size.")
    width: int = Field(..., description="Width of the image.")
    url: str = Field(..., description="URL of the image.")

class VkPhotoSchema(BaseModelConfig):
    id: int = Field(..., description="Vk photo ID (integer)",
                    serialization_alias="vk_id",
                    validation_alias=AliasChoices('id', 'vk_id'))
    album_id: int = Field(..., description="Album ID.")
    date: int = Field(..., description="Date the photo was taken or uploaded.")
    owner_id: int = Field(..., description="Owner ID.")
    access_key: Optional[str] = Field(None, description="Access key for private photos.")
    post_id: Optional[int] = Field(None, description="Post ID the photo is attached to.")
    sizes: List[VkSizeSchema] = Field(..., description="Available sizes of the photo.")
    text: Optional[str] = Field(None, description="Description or text associated with the photo.")
    user_id: Optional[int] = Field(None, description="ID of the user who uploaded the photo.")
    web_view_token: Optional[str] = Field(None, description="Token for web view.")
    has_tags: Optional[bool] = Field(None, description="Indicates if the photo has tags.")
    orig_photo: Optional[VkSizeSchema] = Field(None, description="Original photo details.")

class VkAttachmentSchema(BaseModelConfig):
    type: str = Field(..., description="Type of the attachment (e.g., photo, video).")
    photo: Optional[VkPhotoSchema] = Field(None, description="Photo details, if the attachment is a photo.")

class VkPostSourceSchema(BaseModelConfig):
    platform: Optional[str] = Field(None, description="Platform the post was made from.")
    type: str = Field(..., description="Type of the post source.")

class VkLikesSchema(BaseModelConfig):
    can_like: int = Field(..., description="Whether the user can like the post.")
    count: int = Field(..., description="Number of likes.")
    user_likes: int = Field(..., description="Whether the user liked the post.")
    can_publish: int = Field(..., description="Whether the user can publish the post.")
    repost_disabled: bool = Field(..., description="Indicates if reposting is disabled.")

class VkRepostsSchema(BaseModelConfig):
    count: int = Field(..., description="Number of reposts.")
    user_reposted: int = Field(..., description="Whether the user reposted the content.")

class VkCommentsSchema(BaseModelConfig):
    can_post: Optional[int] = Field(None, description="Whether the user can post comments.")
    can_view: Optional[int] = Field(None, description="Whether the user can view comments.")
    count: Optional[int] = Field(None, description="Number of comments.")
    groups_can_post: Optional[bool] = Field(None, description="Whether groups can post comments.")

class VkPostSchema(BaseModelConfig):
    id: int = Field(..., description="Vk post  ID (integer)",
                    serialization_alias="vk_id",
                    validation_alias=AliasChoices('id', 'vk_id'))
    inner_type: str = Field(..., description="Inner type of the post.")
    ads_easy_promote: Dict[str, Any] = Field(..., description="Promotion-related details.")
    donut: Optional[Dict[str, Any]] = Field(None, description="Donut-related details.")
    comments: Optional[VkCommentsSchema] = Field(None, description="Comments associated with the post.")
    marked_as_ads: int = Field(..., description="Indicates if the post is marked as an ad.")
    attachments: List[VkAttachmentSchema] = Field(..., description="List of attachments associated with the post.")
    date: int = Field(..., description="Timestamp of the post.")
    from_id: int = Field(..., description="ID of the user or group who posted.")
    is_favorite: bool = Field(..., description="Whether the post is marked as favorite.")
    likes: VkLikesSchema = Field(..., description="Likes associated with the post.")
    owner_id: int = Field(..., description="ID of the owner of the post.")
    post_source: VkPostSourceSchema = Field(..., description="Source of the post.")
    post_type: str = Field(..., description="Type of the post (e.g., post, reply).")
    reposts: VkRepostsSchema = Field(..., description="Repost details.")
    text: Optional[str] = Field(None, description="Text content of the post.")
    views: Optional[Dict[str, int]] = Field(None, description="View count of the post.")
    edited: Optional[int] = Field(None, description="Timestamp when the post was last edited.")
    signer_id: Optional[int] = Field(None, description="ID of the user who signed the post.")
    geo: Optional[Dict[str, Any]] = Field(None, description="Geographical information associated with the post.")
    copy_history: Optional[List[Dict[str, Any]]] = Field(None, description="Copy history of the post.")
    can_pin: Optional[int] = Field(None, description="Whether the post can be pinned.")
    can_delete: Optional[int] = Field(None, description="Whether the post can be deleted.")
    can_edit: Optional[int] = Field(None, description="Whether the post can be edited.")
    is_pinned: Optional[int] = Field(None, description="Whether the post is pinned.")
    friends_only: Optional[int] = Field(None, description="Whether the post is visible to friends only.")
    postponed_id: Optional[int] = Field(None, description="ID of the postponed post.")

class VkReactionSetItemSchema(BaseModelConfig):
    id: int = Field(..., description="Vk reaction  ID (integer)",
                    serialization_alias="vk_id",
                    validation_alias=AliasChoices('id', 'vk_id'))
    title: str = Field(..., description="Title of the reaction.")
    asset: Dict[str, Any] = Field(..., description="Asset details for the reaction.")


class VkWallResponseSchema(BaseModelConfig):
    count: int = Field(..., description="Total number of items.")
    items: List[VkPostSchema] = Field(..., description="List of posts.")
    profiles: List[VkUserResponseSchema] = Field(..., description="List of user profiles.")
    groups: List[VkGroupSchema] = Field(..., description="List of groups.")
    next_from: Optional[str] = Field(None, description="Cursor for the next set of results.")

class VkWallRequestSchema(BaseModelConfig):
    owner_id: Optional[int] = Field(None, description="Owner ID of the wall.")
    offset: Optional[int] = Field(None, description="Offset for the wall.")
    count: Optional[int] = Field(None, description="Number of posts to retrieve max 100.")
    filter: Optional[str] = Field(default='All', description="Filter for the wall.")
    extended: Optional[int] = Field(default=1, description="Whether to retrieve extended information.")
    fields: Optional[List[str]] = Field(None, description="List of fields to retrieve.")

    @field_validator("owner_id", mode='before')
    @classmethod
    def validate_owner_id(cls, data: int) -> int:
        if not data < 0:
            return -data
        return data

class VkCommentLikesSchema(BaseModelConfig):
    can_like: int = Field(..., description="Whether the user can like the comment.")
    count: int = Field(..., description="Number of likes.")
    user_likes: int = Field(..., description="Whether the user liked the comment.")
    can_like_by_group: int = Field(..., description="Whether a group can like the comment.")
    author_liked: bool = Field(..., description="Whether the author liked the comment.")


class VkCommentThreadSchema(BaseModelConfig):
    count: int = Field(..., description="Number of replies in the thread.")
    items: List[Dict[str, Any]] = Field(..., description="List of replies (empty if no replies).")
    can_post: bool = Field(..., description="Whether replies can be posted in the thread.")
    show_reply_button: bool = Field(..., description="Whether the reply button is shown.")
    groups_can_post: bool = Field(..., description="Whether groups can post in the thread.")


class VkCommentSchema(BaseModelConfig):
    id: int = Field(..., description="Vk comment ID (integer)",
                    serialization_alias="vk_id",
                    validation_alias=AliasChoices('id', 'vk_id'))
    from_id: int = Field(..., description="ID of the user or group who posted the comment.")
    date: int = Field(..., description="Timestamp of when the comment was posted.")
    text: str = Field(..., description="Text content of the comment.")
    post_id: int = Field(..., description="ID of the post the comment belongs to.")
    owner_id: int = Field(..., description="ID of the owner of the post.")
    parents_stack: List[int] = Field(..., description="Stack of parent comment IDs.")
    likes: VkCommentLikesSchema = Field(..., description="Likes information for the comment.")
    thread: VkCommentThreadSchema = Field(..., description="Thread information for the comment.")


class VkCommentsResponseSchema(BaseModelConfig):
    count: int = Field(..., description="Total number of comments.")
    items: List[VkCommentSchema] = Field(..., description="List of comments.")
    profiles: List[VkUserResponseSchema] = Field(..., description="List of user profiles associated with the comments.")
    groups: List[VkGroupSchema] = Field(..., description="List of groups associated with the comments.")
    current_level_count: int = Field(..., description="Number of comments at the current level.")
    can_post: bool = Field(..., description="Whether the user can post comments.")
    show_reply_button: bool = Field(..., description="Whether the reply button is shown.")
    groups_can_post: bool = Field(..., description="Whether groups can post comments.")
    order: str = Field(..., description="Order of the comments (e.g., 'desc').")
    post_author_id: int = Field(..., description="ID of the author of the post.")
