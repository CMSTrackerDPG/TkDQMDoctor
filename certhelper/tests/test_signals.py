import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError

from mixer.backend.django import mixer

from certhelper.models import UserProfile

pytestmark = pytest.mark.django_db


def test_create_user_profile():
    user = mixer.blend(User)
    assert user.userprofile, "Signal should create a UserProfile"
    with pytest.raises(IntegrityError, message="Only one UserProfile per User allowed"):
        UserProfile.objects.create(user=user)
