import pytest
from vkontakte.models import VkCredentials, VkUser

def test_from_url_valid_url():
    url = 'https://example.com/#access_token=valid_token&expires_in=3600'
    credentials = VkCredentials.from_url(url)
    assert credentials.access_token == 'valid_token'
    assert credentials.expires_in == 3600

def test_create_user():
    user = VkUser(id=1, first_name='John')
    assert user.id == 1
    assert user.first_name == 'John'

def test_create_user_missing_id():
    with pytest.raises(ValueError):
        VkUser(first_name='John')

def test_create_user_missing_first_name():
    with pytest.raises(ValueError):
        VkUser(id=1)