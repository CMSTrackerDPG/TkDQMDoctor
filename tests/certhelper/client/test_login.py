import pytest
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from mixer.backend.django import mixer

from tests.credentials import PASSWORD

pytestmark = pytest.mark.django_db


def test_shifter_is_shift_leader_after_login(client, shifter):
    user = User.objects.get()
    assert not user.is_staff
    assert user.userprofile.is_shifter
    assert not user.userprofile.is_shiftleader

    extra_data = {"groups": ["tkdqmdoctor-shiftleaders"]}
    mixer.blend(SocialAccount, user=user, extra_data=extra_data)

    user = User.objects.get()
    assert not user.is_staff
    assert user.userprofile.is_shifter
    assert not user.userprofile.is_shiftleader

    assert client.login(username=user.username, password=PASSWORD)

    user = User.objects.get()
    assert user.is_staff
    assert not user.userprofile.is_shifter
    assert user.userprofile.is_shiftleader


def test_user_is_admin_after_login(client):
    user = User.objects.create_superuser(username="Klaus", password=PASSWORD, email="")
    assert user.userprofile.is_guest
    assert not user.userprofile.is_admin

    extra_data = {"groups": ["tkdqmdoctor-admins"]}
    mixer.blend(SocialAccount, user=user, extra_data=extra_data)

    user = User.objects.get()
    assert user.userprofile.is_guest
    assert not user.userprofile.is_admin

    assert client.login(username=user.username, password=PASSWORD)
    user = User.objects.get()
    assert not user.userprofile.is_guest
    assert user.userprofile.is_admin
