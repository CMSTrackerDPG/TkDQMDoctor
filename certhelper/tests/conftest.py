import logging

import pytest
from selenium import webdriver

# Disables Logging when testing
logging.disable(logging.CRITICAL)


SUPERUSER_USERNAME = "superuser"
SHIFTER1_USERNAME = "shifter1"
SHIFTER2_USERNAME = "shifter2"
SHIFTLEADER_USERNAME = "shiftleader1"
EXPERT_USERNAME = "expert1"
ADMIN_USERNAME = "admin"

PASSWORD = "VerySecurePasswort"


@pytest.fixture
def superuser(django_user_model):
    """returns a user with superuser rights"""
    return django_user_model.objects.create_superuser(
        username=SUPERUSER_USERNAME,
        password=PASSWORD,
        email=""
    )


@pytest.fixture
def shifter(django_user_model):
    user = django_user_model.objects.create(username=SHIFTER1_USERNAME)
    user.set_password(PASSWORD)
    user.userprofile.extra_data = {"groups": ["tkdqmdoctor-shifters"]}
    user.userprofile.upgrade_user_privilege()
    user.save()
    return user


@pytest.fixture
def second_shifter(django_user_model):
    user = django_user_model.objects.create(username=SHIFTER2_USERNAME)
    user.set_password(PASSWORD)
    user.userprofile.extra_data = {"groups": ["tkdqmdoctor-shifters"]}
    user.userprofile.upgrade_user_privilege()
    user.save()
    return user


@pytest.fixture
def shiftleader(django_user_model):
    user = django_user_model.objects.create(username=SHIFTLEADER_USERNAME)
    user.set_password(PASSWORD)
    user.userprofile.extra_data = {"groups": ["tkdqmdoctor-shiftleaders"]}
    user.userprofile.upgrade_user_privilege()
    user.save()
    return user


@pytest.fixture
def expert(django_user_model):
    user = django_user_model.objects.create(username=EXPERT_USERNAME)
    user.set_password(PASSWORD)
    user.userprofile.extra_data = {"groups": ["tkdqmdoctor-experts"]}
    user.userprofile.upgrade_user_privilege()
    user.save()
    return user


@pytest.fixture
def admin(django_user_model):
    user = django_user_model.objects.create(username=ADMIN_USERNAME)
    user.set_password(PASSWORD)
    user.userprofile.extra_data = {"groups": ["tkdqmdoctor-admins"]}
    user.userprofile.upgrade_user_privilege()
    user.save()
    return user


@pytest.fixture
def firefox():
    """returns a Firefox browser webdriver instance"""
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    firefox_webdriver = webdriver.Firefox(firefox_options=options)
    firefox_webdriver.implicitly_wait(60)
    yield firefox_webdriver
    firefox_webdriver.quit()


@pytest.fixture
def authenticated_browser(firefox, client, live_server, superuser):
    """returns a firefox browser instance with logged-in superuser"""
    client.login(username=SUPERUSER_USERNAME, password=PASSWORD)
    cookie = client.cookies['sessionid']

    firefox.get(live_server.url)
    firefox.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
    firefox.refresh()

    return firefox
