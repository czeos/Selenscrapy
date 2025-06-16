from typing import Optional, List, Type
from pydantic import BaseModel, ConfigDict
from vk_api import VkApi, ApiError, LoginRequired, AuthError
from config import VkConfig
from vkontakte.vk_api_schema import VkUserResponseSchema, VkUserFriendLis, VkScreenNameResolveResponse, VkUserRequestSchema
from neogr_model.client import Neo4jClient
from vkontakte.logger import vk_logger
from vkontakte.auth import authentication_with_state, save_authentication_state
from config import setting
from vkontakte.utils import update_vk_credentials
from neogr_model.model import VkUserNode

## vk client
class VkClient(BaseModel):
    config: VkConfig
    session: Optional[VkApi] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def authenticate(self):
        try:
            self.session = VkApi(token=self.config.ACCESS_TOKEN)
            self.session.method('account.getProfileInfo')
            vk_logger.info("Authentication successful.")
            update_vk_credentials(self.config)
        except (LoginRequired, ApiError) as e:
            vk_logger.error(f"Authentication failed with the provided token: ({self.config.ACCESS_TOKEN}): {str(e)}")
            self._auth_with_state()


    def _auth_with_state(self):
        try:
            self.config.ACCESS_TOKEN = authentication_with_state(login=self.config.LOGIN)
            self.authenticate()
        except (Exception, FileExistsError) as e:
            self._get_auth_state()

    def _get_auth_state(self):
        save_authentication_state(login=self.config.LOGIN, password=self.config.PWD)
        self._auth_with_state()

    def method(self, method: str, request: dict):
        try:
            return self.session.method(method, request)
        except Exception as e:
            self.authenticate()
            return self.session.method(method, request)

# initialize the VkClient
try:
    vk_client = VkClient(config=setting.vkontakte)
    vk_client.authenticate()
except AuthError as e:
    vk_logger.error(f"Authentication failed: {str(e)}")
    raise e


# function to scrape vk data
def scrape_vk_entity(vk_client: VkClient, method: str, request: BaseModel, responseSchema: Type[BaseModel]) -> BaseModel:
    """
    General method for interaction with VK API
    Scrape VK data entity, interaction with concrete VK API method
    :param vk_client: VkClient
    :param method: str
    :param request: BaseModel
    :param responseSchema: Type[BaseModel]
    """
    response = vk_client.method(method, request.model_dump())
    try:
        return responseSchema(**response)
    except TypeError:
        return responseSchema(**response[0])


def get_fields_from_schema(schema: Type[BaseModel]) -> list[str]:
    """
    Get fields from Pydantic schema
    """
    return [field for field in schema.model_fields.keys()]


def get_user_info(vk_client: VkClient, user_id: int, ) -> VkUserResponseSchema:
    """
    Get user profile information
    :param vk_client:
    :param user_id:
    :return:
    """
    request = VkUserRequestSchema(user_ids=user_id, fields= ','.join(get_fields_from_schema(VkUserResponseSchema)))
    return scrape_vk_entity(vk_client, 'users.get', request, VkUserResponseSchema)


def get_user_friend_lists(vk_client: VkClient, user_id: int) -> List[VkUserFriendLis]:
    """
    Get user friend lists
    :param vk_client:
    :param user_id:
    :return:
    """
    request = VkUserRequestSchema(user_id=user_id)
    return scrape_vk_entity(vk_client, 'friends.getLists', request, VkUserFriendLis)


def get_user_friends(vk_client: VkClient, user_id: int, list_id: Optional[int], fields: Optional[list[str]] = None) -> List[VkUserResponseSchema]:
    """
    Get all users friends
    :param vk_client:
    :param user_id:
    :param order:
    :param list_id:
    :param fields:
    :return:
    """
    if fields is None:
        fields = [field for field in VkUserResponseSchema.model_fields.keys()]
    request = VkUserRequestSchema(user_id=user_id, list_id=list_id, fields=','.join(fields))
    return scrape_vk_entity(vk_client, 'friends.get', request, VkUserResponseSchema)


class VkUserAPI(BaseModel):
    """
    TODO: Add other export methods exept the Neo4j
    """
    id: int
    vk_client: VkClient
    neo_client: Optional[Neo4jClient] = None
    profile: Optional[VkUserResponseSchema] = None
    friend_lists: Optional[List[VkUserFriendLis]] = None
    friends: Optional[List[VkUserResponseSchema]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def get_user_info(self, fields: Optional[list[str]] = None) -> None:
        """
        Get user profile information
        :param fields:
        :return:
        """
        if fields is None:
            fields = [field for field in VkUserResponseSchema.model_fields.keys()]
        response = self.vk_client.method('users.get', {'user_ids': self.id, 'fields': ','.join(fields)})
        self.profile=VkUserResponseSchema(**response[0])

    def get_user_friend_lists(self) -> None:
        """
        Get user friend lists
        :return:
        """
        response = self.vk_client.method('friends.getLists', {'user_id': self.id})
        self.friend_lists = [VkUserFriendLis(**friend_list) for friend_list in response['items']]

    def ger_user_friends(self, order: str ='name', list_id: Optional[int] = None, fields: Optional[list[str]] = None) -> None:
        """
        Get all users friends
        TODO: implement ordering via Enum
        :param fields:
        :return:
        """
        if fields is None:
            fields = [field for field in VkUserResponseSchema.model_fields.keys()]
        response = self.vk_client.method(method='friends.get',
                                         payload={'user_id': self.id,
                                               'list_id': list_id,
                                               'order': order,
                                               'fields': ','.join(fields)})
        if response.get('count') >= 5000:
            raise NotImplementedError('This user has more than 5000 friends. Paging is not implemented yet')
        self.friends = [VkUserResponseSchema(**user) for user in response['items']]

    def save_user_to_neo4j(self) -> VkUserNode:
        """
        Save the user's profile and their friends to Neo4j.
        """
        if not self.neo_client:
            raise ValueError("Neo4jClient is not initialized.")
        if not self.profile:
            raise ValueError("Profile is not populated. Call `get_user_info()` first.")

        # Save the  user profile (Pydantic Schema) to Neo4j
        return self.neo_client.create_or_update_node(VkUserNode, self.profile)

    def save_user_friends_to_neo4j(self, user_node: VkUserNode) -> None:
        """
        Save the user's friends to Neo4j.
        :return:
        """
        # Save friends and create relationships
        if self.friends:
            for friend in self.friends:
                friend_node = self.neo_client.create_or_update_node(VkUserNode, friend)
                self.neo_client.create_relationship(user_node, "friends", friend_node)

    def load_user_from_neo4j(self) -> Optional[VkUserResponseSchema]:
        """
        Load the user's profile from Neo4j into `self.profile`.
        """
        if not self.neo_client:
            raise ValueError("Neo4jClient is not initialized.")

        node = self.neo_client.get_node(VkUserNode, id=self.id)
        if node:
            self.profile = VkUserResponseSchema(**node.__properties__)
        return self.profile

    def load_friends_from_neo4j(self) -> Optional[List[VkUserResponseSchema]]:
        """
        Load the user's friends from Neo4j into `self.friends`.
        """
        if not self.neo_client:
            raise ValueError("Neo4jClient is not initialized.")

        node = self.neo_client.get_node(VkUserNode, id=self.id)
        if node:
            friends = self.neo_client.get_related_nodes(node, "friends")
            self.friends = [
                VkUserResponseSchema(**friend.__properties__)
                for friend in friends
            ]
        return self.friends

    def delete_user_from_neo4j(self) -> None:
        """
        Delete the user from Neo4j.
        """
        if not self.neo_client:
            raise ValueError("Neo4jClient is not initialized.")

        self.neo_client.delete_node(VkUserNode, id=self.id)



if __name__ == '__main__':
    from vkontakte.vk_api_schema import VkWallRequestSchema, VkWallResponseSchema
    screen_name_url = 'https://vk.com/vladimirskilager29760'
    screen_name = 'vladimirskilager29760'
    group_id = 33438842

    # # get wall
    # request = VkWallRequestSchema(owner_id=group_id, count=10)
    # response = scrape_vk_entity(vk_client, 'wall.get', request, VkWallResponseSchema)
    # pass

    from vkontakte.vk_api_schema import VkUserRequestSchema, VkUserResponseSchema
    request = VkUserRequestSchema(user_ids=612442580)
    response = scrape_vk_entity(vk_client, 'users.get', request, VkUserResponseSchema)


    # user_request = VkUserAPI(id=1, vk_client=vk_client, neo_client=neo_client)
    # user_request.get_user_info(fields=['city', 'country