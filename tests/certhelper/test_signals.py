import pytest
from django.db import IntegrityError
from mixer.backend.django import mixer

from certhelper.signals import *

pytestmark = pytest.mark.django_db


def test_create_user_profile():
    user = mixer.blend(User)
    user.userprofile.extra_data = {"hi": "test"}
    assert user.userprofile
    with pytest.raises(IntegrityError, message="Only one UserProfile per User allowed"):
        UserProfile.objects.create(user=user)


def test_logs():
    """
    Just run them once, nothing really to test here
    """
    log_user_logged_in(None, None, None)
    log_user_logged_out(None, None, None)
    log_user_has_login_failed(None, None, None)
    log_allauth_user_logged_in(None, None)
    log_pre_social_login(None, None)
    log_social_account_added(None, None)
    log_social_account_updated(None, None)
    log_social_account_removed(None, None)


def test_userprofile_automatically_created():
    user = mixer.blend(User)
    assert user.userprofile


def test_update_users_userprofile_on_save():
    user = mixer.blend(User)
    assert not user.is_staff
    assert not user.is_superuser
    assert user.userprofile.is_guest
    user.save()
    assert user.userprofile.is_guest
    extra_data = {"groups": ["tkdqmdoctor-admins"]}
    mixer.blend(SocialAccount, user=user, extra_data=extra_data)
    assert user.userprofile.is_guest
    assert not user.is_staff
    assert not user.is_superuser

    user.save()
    assert not user.userprofile.is_guest
    assert user.is_staff
    assert user.is_superuser

    user = User.objects.get()
    assert not user.userprofile.is_guest
    assert user.is_staff
    assert user.is_superuser
