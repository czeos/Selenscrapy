import shutil
import toml
from filelock import FileLock

from config import CONFIG_PATH, setting
from vkontakte.api_schema import VkCredentialsResponse


def update_vk_credentials(credentials: VkCredentialsResponse):
    """
    Update VK credentials in the config file. Url token can be obtained from the website https://vkhost.github.io/
    Login and password can be used to get the token (not implemented yet).
    :param credentials:
    :return:
    """
    temp_config_path = CONFIG_PATH.with_suffix('.tmp')
    lock = FileLock(f"{CONFIG_PATH}.lock")
    try:
        with lock:
            setting.vkontakte = credentials
            with open(temp_config_path, 'w') as file:
                toml.dump(setting.model_dump(), file)
            shutil.move(temp_config_path, CONFIG_PATH)
        return credentials
    except Exception as e:
        if temp_config_path.exists():
            temp_config_path.unlink()
