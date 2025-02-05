import pytest
from pydantic import ValidationError

from vkontakte.vk_api_schema import VkUserSchema
from vkontakte.scrapers import VkClient

def from_url_invalid_url():
    url = 'https://example.com/#invalid_token'
    with pytest.raises(ValueError):
        VkClient.from_url(url)

def test_create_user_with_all_fields():
    user = VkUserSchema(id=1, first_name='John', last_name='Doe', deactivated='banned', about='About me',
                        activities='Activities', bdate='01.01.2000', blacklisted=1, books='Books',
                        can_access_closed=1, can_see_all_posts=1, can_see_audio=1, domain='johndoe',
                        followers_count=100, games='Games', has_mobile=1, has_photo=1, home_town='Hometown',
                        interests='Interests', is_closed=True, is_hidden_from_feed=1, maiden_name='Maiden',
                        movies='Movies', music='Music', nickname='Nickname', photo_id='photo123',
                        photo_max_orig='photo_max_url', quotes='Quotes', relation=1, screen_name='screenname',
                        sex=1, site='https://example.com', status='Status', timezone=3, tv='TV', verified=1)
    assert user.id == 1
    assert user.first_name == 'John'
    assert user.last_name == 'Doe'
    assert user.deactivated == 'banned'
    assert user.about == 'About me'
    assert user.activities == 'Activities'
    assert user.bdate == '2000-01-01T00:00:00'
    assert user.blacklisted is True
    assert user.books == 'Books'
    assert user.can_access_closed is True
    assert user.can_see_all_posts == 1
    assert user.can_see_audio is True
    assert user.domain == 'johndoe'
    assert user.followers_count == 100
    assert user.games == 'Games'
    assert user.has_mobile is True
    assert user.has_photo is True
    assert user.home_town == 'Hometown'
    assert user.interests == 'Interests'
    assert user.is_closed is True
    assert user.is_hidden_from_feed is True
    assert user.maiden_name == 'Maiden'
    assert user.movies == 'Movies'
    assert user.music == 'Music'
    assert user.nickname == 'Nickname'
    assert user.photo_id == 'photo123'
    assert user.photo_max_orig == 'photo_max_url'
    assert user.quotes == 'Quotes'
    assert user.relation == 'not married'
    assert user.screen_name == 'screenname'
    assert user.sex == 'female'
    assert user.site == 'https://example.com'
    assert user.status == 'Status'
    assert user.timezone == 3
    assert user.tv == 'TV'
    assert user.verified is True

def test_create_user_with_invalid_bdate():
    with pytest.raises(ValidationError):
        VkUserSchema(id=1, first_name='John', bdate='invalid_date')

def test_create_user_with_partial_bdate():
    user = VkUserSchema(id=1, first_name='John', bdate='01.01')
    assert user.bdate == '1900-01-01T00:00:00'

def test_create_user_with_invalid_relation():
    with pytest.raises(KeyError):
        VkUserSchema(id=1, first_name='John', relation=9)

def test_create_user_with_invalid_sex():
    with pytest.raises(KeyError):
        VkUserSchema(id=1, first_name='John', sex=3)