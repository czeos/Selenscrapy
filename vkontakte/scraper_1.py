from enum import Enum
import vk_api as vk
from vk_api.exceptions import ApiError

from vkontakte.models import Wall, VkUser, VkEntityBase
from vkontakte.scrapers import VkClient, VkUserAPI

def resolve_vk_object_from_link(client, screen_name):
    try:
        vk =  client.get_api()
        response = vk.utils.resolveScreenName(screen_name=screen_name)
        if response:
            return response  # This contains 'type' and 'object_id'
        else:
            return "Invalid or non-existent screen name."
    except ApiError as e:
        return f"VK API Error: {e}"

def get_wall_posts(vk_client, user_id):
    response = vk_client.method('wall.get', {'owner_id': user_id})
    return Wall(**response, owner_id=user_id)

def get_group_posts(client, group_id, max_posts=10):
    response = client.method('wall.get', {'owner_id': -group_id, 'count': max_posts})

    return Wall(**response, owner_id=group_id)



if __name__ == '__main__':
    from config import Config, CONFIG_PATH
    from vkontakte.scrapers import VkClient
    from db import Neo4jClient

    config = Config(config_path=CONFIG_PATH)

    vk_client = VkClient.from_url(config.vkontakte.AUTH_URL)
    neo_client = Neo4jClient(uri=config.neo4j.URI,
                             username=config.neo4j.USERNAME,
                             password=config.neo4j.PASSWORD,
                             db_name=config.neo4j.DB_NAME)

    user = VkUserAPI(id=5845531, vk_client=vk_client, neo_client=neo_client)
    user.get_user_info() # get user info
    # user.get_user_friend_lists()
    user.ger_user_friends()
    user.save_user_to_neo4j()
    pass

    # group_posts = get_group_posts(client,33438842, 10)
    # posts = get_wall_posts(client,896119729)
    # friends = get_friends(client,5845531)
    # profile_info = profile_info(client,5845531, USER_INFO_FIELDS)

    pass

