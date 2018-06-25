import pytest
from django.db import IntegrityError
from mixer.backend.django import mixer

from certhelper.signals import *

pytestmark = pytest.mark.django_db


def test_create_user_profile():
    user = mixer.blend(User)
    assert user.userprofile, "Signal should create a UserProfile"
    with pytest.raises(IntegrityError, message="Only one UserProfile per User allowed"):
        UserProfile.objects.create(user=user)


def test_update_user_privilege_by_e_groups():
    update_newly_added_user_privilege_by_e_groups(None, None)
    update_user_privilege_by_e_groups(request=None, user=None)

    assert len(UserProfile.objects.all()) == 0
    assert len(User.objects.all()) == 0

    class Object(object):
        """Dummy class to simulate a SocialLogin"""
        pass

    socialaccount = mixer.blend(SocialAccount)
    sociallogin = Object()
    sociallogin.account = socialaccount
    sociallogin.user = socialaccount.user
    socialaccount.user.save()

    update_newly_added_user_privilege_by_e_groups(None, sociallogin)
    assert len(UserProfile.objects.all()) == 1
    assert len(User.objects.all()) == 1

    update_user_privilege_by_e_groups(None, socialaccount.user)
    sociallogin.user.save()
    assert len(UserProfile.objects.all()) == 1
    assert len(User.objects.all()) == 1


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
