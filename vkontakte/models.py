from typing import Optional, List, Dict, Any, Type, Union
from pydantic import BaseModel, Field, model_validator, ConfigDict, field_validator

class VkEntityBase(BaseModel):
    model_config = ConfigDict(extra='ignore')


class LastSeen(VkEntityBase):
    time: Optional[int]
    platform: Optional[int]

class CropPhoto(VkEntityBase):
    photo: Optional[dict]
    crop: Optional[dict]
    rect: Optional[dict]

class Occupation(VkEntityBase):
    type: Optional[str]
    name: Optional[str]

class Relative(VkEntityBase):
    id: Optional[int]
    type: Optional[str]

class Personal(VkEntityBase):
    political: Optional[int]
    langs: Optional[List[str]]
    religion: Optional[str]
    inspired_by: Optional[str]
    people_main: Optional[int]
    life_main: Optional[int]
    smoking: Optional[int]
    alcohol: Optional[int]

class University(VkEntityBase):
    id: Optional[int]
    country: Optional[int]
    city: Optional[int]
    name: Optional[str]
    faculty: Optional[int]
    faculty_name: Optional[str]
    chair: Optional[int]
    chair_name: Optional[str]
    graduation: Optional[int]
    education_form: Optional[str]
    education_status: Optional[str]

class School(VkEntityBase):
    id: Optional[int]
    country: Optional[int]
    city: Optional[int]
    name: Optional[str]
    year_from: Optional[int]
    year_to: Optional[int]
    year_graduated: Optional[int]
    class_letter: Optional[str]
    speciality: Optional[str]
    type: Optional[int]
    type_str: Optional[str]

class Career(VkEntityBase):
    group_id: Optional[int]
    company: Optional[str]
    country_id: Optional[int]
    city_id: Optional[int]
    city_name: Optional[str]
    from_year: Optional[int]
    until_year: Optional[int]
    position: Optional[str]

class Military(VkEntityBase):
    unit: Optional[str]
    unit_id: Optional[int]
    country_id: Optional[int]
    from_year: Optional[int]
    until_year: Optional[int]

class VkUser(VkEntityBase):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    deactivated: Optional[str] = None
    hidden: Optional[int] = None
    sex: Optional[int] = None
    screen_name: Optional[str] = None
    photo_50: Optional[str] = None
    photo_100: Optional[str] = None
    photo_200_orig: Optional[str] = None
    photo_200: Optional[str] = None
    photo_400_orig: Optional[str] = None
    photo_max: Optional[str] = None
    photo_max_orig: Optional[str] = None
    online: Optional[int] = None
    online_mobile: Optional[int] = None
    online_app: Optional[int] = None
    verified: Optional[int] = None
    trending: Optional[int] = None
    friend_status: Optional[int] = None
    mutual_friends: Optional[List[int]] = None
    bdate: Optional[str] = None
    home_town: Optional[str] = None
    has_photo: Optional[int] = None
    has_mobile: Optional[int] = None
    is_friend: Optional[int] = None
    can_post: Optional[int] = None
    can_see_all_posts: Optional[int] = None
    can_see_audio: Optional[int] = None
    can_write_private_message: Optional[int] = None
    can_send_friend_request: Optional[int] = None
    mobile_phone: Optional[str] = None
    home_phone: Optional[str] = None
    site: Optional[str] = None
    status: Optional[str] = None
    last_seen: Optional[LastSeen] = None
    crop_photo: Optional[CropPhoto] = None
    followers_count: Optional[int] = None
    common_count: Optional[int] = None
    occupation: Optional[Occupation] = None
    nickname: Optional[str] = None
    relatives: Optional[List[Relative]] = None
    relation: Optional[int] = None
    personal: Optional[Personal] = None
    connections: Optional[dict] = None
    exports: Optional[dict] = None
    activities: Optional[str] = None
    interests: Optional[str] = None
    music: Optional[str] = None
    movies: Optional[str] = None
    tv: Optional[str] = None
    books: Optional[str] = None
    games: Optional[str] = None
    universities: Optional[List[University]] = None
    schools: Optional[List[School]] = None
    about: Optional[str] = None
    quotes: Optional[str] = None
    career: Optional[List[Career]] = None
    military: Optional[List[Military]] = None


class Photo(VkEntityBase):
    access_key: Optional[str] = None
    album_id: Optional[int] = None
    date: Optional[int] = None
    id: Optional[int] = None
    post_id: Optional[int] = None
    owner_id: Optional[int] = None
    post_id: Optional[int] = None
    text: Optional[str] = ""
    user_id: Optional[int] = None
    web_view_token: Optional[str] = None
    lat: Optional[float] = None
    long: Optional[float] = None
    orig_photo: Optional[Dict[str, Any]] = None


class Place(VkEntityBase):
    checkins: int
    country: int
    created: int
    discriminator: str
    icon: str
    id: int
    latitude: float
    longitude: float
    title: str
    type: int

class GeoData(VkEntityBase):
    coordinates: str
    place: Place
    type: str


class VkAttachmentRegister(VkEntityBase):
    reg: Dict[str, Any] = Field(default_factory=dict)

    def register(self, key: str, attachment: Type[VkEntityBase]):
        self.reg[key] = attachment

    def attachment2model(self, data: dict) -> VkEntityBase:
        attachment_type = data.get('type')
        attachment_model = self.reg.get(attachment_type)
        if attachment_model:
            try:
                return attachment_model(**data[attachment_type])
            except KeyError:
                print(KeyError(f'VKAttachmentRegister: Could not find {attachment_type} in {data}'))

attachment_register = VkAttachmentRegister()
attachment_register.register('photo', Photo)
attachment_register.register('geo', GeoData)

class Message(VkEntityBase):
    id: int
    from_id: int
    owner_id: int
    date: int
    text: Optional[str] = None
    signer_id: Optional[int] = None
    is_pinned: Optional[bool] = None
    can_pin: Optional[bool] = None
    can_delete: Optional[bool] = None
    can_edit: Optional[bool] = None
    post_type: Optional[str] = None
    attachments: List[Union[Photo, GeoData]] | None = None
    comments: Optional[Dict[str, Any]] = None
    likes: Optional[Dict[str, Any]] = None
    geo: Optional[Dict[str, Any]] = None
    reposts: Optional[Dict[str, Any]] = None
    views: Optional[Dict[str, Any]] = None
    post_source: Optional[Dict[str, Any]]
    created_by: VkUser

    @model_validator(mode='before')
    @classmethod
    def set_created_by(cls, values):
        from_id = values.get('from_id')
        attachments = values.get('attachments')
        if from_id:
            values['created_by'] = VkUser(id=from_id)
        if not attachments:
            values['attachments'] = None
        else:
            values['attachments'] = [attachment_register.attachment2model(attachment) for attachment in attachments]

        return values



class Wall(VkEntityBase):
    owner_id: int
    posts: List[Message]
    count: int

    @model_validator(mode='before')
    def validate_posts(cls, values):
        items = values.get('items', [])
        try:
            values['posts'] = [Message(**item) for item in items]
        except Exception as e:
            print(f"Error processing posts: {e}")
            raise
        return values
