import vk_api

from vkontakte.models import VkCredentials


def resolve_vk_link(vk, screen_name):
    try:
        response = vk.utils.resolveScreenName(screen_name=screen_name)
        if response:
            return response  # This contains 'type' and 'object_id'
        else:
            return "Invalid or non-existent screen name."
    except vk_api.exceptions.ApiError as e:
        return f"VK API Error: {e}"


def get_vk_server_time(vk_client):
    try:
        response = vk_client.utils.getServerTime()
        return response
    except vk_api.exceptions.ApiError as e:
        print(f"VK API Error: {e}")
        return None

# Example usage
if __name__ == "__main__":
    AUTH_URL = 'https://oauth.vk.com/blank.html#access_token=vk1.a.l8BAh98f1ZS4EK3zSa5xdt6gSpAUd8Ih3xO1TesrkuhEJqh2dQnhcxjUe0DI44W0JpV1HBZDsjnWCGSgdub9YPx9yVlOBt1T1K3shbCme4X3FZuM6FXT3iMMVYW2GzYZHCJ16I39Y0Kf6ZIIQLOHKXbF-7_zdB2xbkEY0xqpCLKIgIy84_mNBbkRysQxSwOImtsqWYc4HXrYj2fLEdzPsA&expires_in=86400&user_id=896119729'
    credential = VkCredentials.from_url(AUTH_URL)
    vk_session = vk_api.VkApi(token=credential.access_token)
    vk = vk_session.get_api()

    server_time = get_vk_server_time(vk)
    print(f"VK Server Time: {server_time}")

    screen_name = "vanysever"  # Extract this from the VK link
    result = resolve_vk_link(vk, screen_name)
    print(result)
