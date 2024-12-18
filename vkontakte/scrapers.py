from typing import Optional, Type, List
from urllib.parse import urlparse, parse_qs
from pydantic import BaseModel, ConfigDict
from vk_api import VkApi

from vkontakte.models import VkEntityBase
from vkontakte.scraper_schema import VkUserSchema, VkUserFriendLis
from db import Neo4jClient, VkUser

class VkClient(BaseModel):
    login: Optional[str] = None
    pwd: Optional[str] = None
    access_token: Optional[str] = None
    expires_in: Optional[int] = None
    session: Optional[VkApi] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_url(cls, url: str):
        parsed_url = urlparse(url)
        fragment = parse_qs(parsed_url.fragment)
        token = fragment.get('access_token', [''])[0]
        expired_in = fragment.get('expires_in', [0])[0]
        session = VkApi(token=token)
        return cls(access_token=token, expires_in=int(expired_in), session=session)

    @classmethod
    def from_credentials(cls, login:str, pwd:str):
        raise NotImplemented('This method is not implemented yet')
        session = VkApi(login=login, password=pwd)
        session.auth(token_only=True)
        return cls(login=login, pwd=pwd, session=session)

    def get_api(self):
        return self.session.get_api()

    def method(self, method: str, payload: dict):
        return self.session.method(method, payload)


def call_vk_method(client, method: str, payload: Type[BaseModel], model: Type[VkEntityBase]):
    response = client.method(method, payload.model_dump())
    return model(**response)


class VkUserAPI(BaseModel):
    """
    TODO: Add other export methods exept the Neo4j
    """
    id: int
    vk_client: VkClient
    neo_client: Optional[Neo4jClient] = None
    profile: Optional[VkUserSchema] = None
    friend_lists: Optional[List[VkUserFriendLis]] = None
    friends: Optional[List[VkUserSchema]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def get_user_info(self, fields: Optional[list[str]] = None) -> None:
        """
        Get user profile information
        :param fields:
        :return:
        """
        if fields is None:
            fields = [field for field in VkUserSchema.model_fields.keys()]
        response = self.vk_client.method('users.get', {'user_ids': self.id, 'fields': ','.join(fields)})
        self.profile=VkUserSchema(**response[0])

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
            fields = [field for field in VkUserSchema.model_fields.keys()]
        response = self.vk_client.method(method='friends.get',
                                         payload={'user_id': self.id,
                                               'list_id': list_id,
                                               'order': order,
                                               'fields': ','.join(fields)})
        if response.get('count') >= 5000:
            raise NotImplementedError('This user has more than 5000 friends. Paging is not implemented yet')
        self.friends = [VkUserSchema(**user) for user in response['items']]

    def save_user_to_neo4j(self) -> None:
        """
        Save the user's profile and their friends to Neo4j.
        """
        if not self.neo_client:
            raise ValueError("Neo4jClient is not initialized.")
        if not self.profile:
            raise ValueError("Profile is not populated. Call `get_user_info()` first.")

        # Save the  user profile (Pydantic Schema) to Neo4j
        user_node = self.neo_client.create_or_update_node(VkUser, self.profile.model_dump(by_alias=True))

        # Save friends and create relationships
        if self.friends:
            for friend in self.friends:
                friend_node = self.neo_client.create_or_update_node(VkUser, friend.model_dump(by_alias=True))
                self.neo_client.create_relationship(user_node, "friends", friend_node)

    def load_user_from_neo4j(self) -> Optional[VkUserSchema]:
        """
        Load the user's profile from Neo4j into `self.profile`.
        """
        if not self.neo_client:
            raise ValueError("Neo4jClient is not initialized.")

        node = self.neo_client.get_node(VkUser, id=self.id)
        if node:
            self.profile = VkUserSchema(id=node.id, first_name=node.first_name, last_name=node.last_name)
        return self.profile

    def load_friends_from_neo4j(self) -> Optional[List[VkUserSchema]]:
        """
        Load the user's friends from Neo4j into `self.friends`.
        """
        if not self.neo_client:
            raise ValueError("Neo4jClient is not initialized.")

        node = self.neo_client.get_node(VkUser, id=self.id)
        if node:
            friends = self.neo_client.get_related_nodes(node, "friends")
            self.friends = [
                VkUserSchema(id=friend.id, first_name=friend.first_name, last_name=friend.last_name)
                for friend in friends
            ]
        return self.friends

    def delete_user_from_neo4j(self) -> None:
        """
        Delete the user from Neo4j.
        """
        if not self.neo_client:
            raise ValueError("Neo4jClient is not initialized.")

        self.neo_client.delete_node(VkUser, id=self.id)
