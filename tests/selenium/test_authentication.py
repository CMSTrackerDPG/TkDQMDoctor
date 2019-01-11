from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User

from tests.credentials import *
from tests.utils.selenium_utilities import try_to_login_user
from mixer.backend.django import mixer

from tests.utils.wait import wait_until


class TestAuthentication:
    def test_anonymous(self, live_server, firefox):
        firefox.get("{}".format(live_server.url))
        assert firefox.title == "TkDQMDoctor: List"
        assert "Login" in firefox.page_source
        assert "Admin Settings" not in firefox.page_source
        assert "Shift Leader" not in firefox.page_source

    def test_login_superuser(self, live_server, firefox, superuser):
        firefox.get("{}".format(live_server.url))
        try_to_login_user(firefox, SUPERUSER_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Admin Settings")
        assert "Admin Settings" in firefox.page_source
        assert "Shift Leader" in firefox.page_source

    def test_login_shiftleader(self, live_server, firefox, shiftleader):
        firefox.get("{}".format(live_server.url))
        try_to_login_user(firefox, SHIFTLEADER_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Admin Settings")
        assert "Admin Settings" in firefox.page_source
        assert "Shift Leader" in firefox.page_source

    def test_login_shifter(self, live_server, firefox, shifter, second_shifter):
        firefox.get("{}".format(live_server.url))
        try_to_login_user(firefox, SHIFTER1_USERNAME, PASSWORD)
        wait_until(
            firefox.find_element_by_link_text, "Logout {}".format(SHIFTER1_USERNAME)
        )
        assert "Admin Settings" not in firefox.page_source
        assert "Shift Leader" not in firefox.page_source
        firefox.find_element_by_link_text("Logout {}".format(SHIFTER1_USERNAME)).click()

        firefox.get("{}".format(live_server.url))
        try_to_login_user(firefox, SHIFTER2_USERNAME, PASSWORD)
        wait_until(
            firefox.find_element_by_link_text, "Logout {}".format(SHIFTER2_USERNAME)
        )
        firefox.find_element_by_link_text("Logout {}".format(SHIFTER2_USERNAME)).click()

        assert "Admin Settings" not in firefox.page_source
        assert "Shift Leader" not in firefox.page_source

    def test_shifter_is_shiftleader_after_login(
        self, live_server, firefox, shifter, superuser
    ):
        user = shifter
        assert not user.is_staff
        assert not user.is_superuser
        assert user.userprofile.is_shifter
        assert not user.userprofile.is_shiftleader

        firefox.get("{}".format(live_server.url))
        try_to_login_user(firefox, superuser.username, PASSWORD)

        wait_until(firefox.find_element_by_link_text, "Admin Settings")
        firefox.find_element_by_link_text("Admin Settings").click()

        wait_until(firefox.find_element_by_link_text, "Social accounts")
        firefox.find_element_by_link_text("Social accounts").click()

        assert "0 social accounts" in firefox.page_source

        wait_until(firefox.find_element_by_link_text, "Home")
        firefox.find_element_by_link_text("Home").click()

        wait_until(firefox.find_element_by_link_text, "Users")
        firefox.find_element_by_link_text("Users").click()

        wait_until(firefox.find_element_by_link_text, "shifter1")
        firefox.find_element_by_link_text("shifter1").click()

        userprofile_text = firefox.find_element_by_id("userprofile-0").text

        assert "Guest" not in userprofile_text
        assert "Shifter" in userprofile_text
        assert "Shift Leader" not in userprofile_text
        assert "tkdqmdoctor-shifters" in userprofile_text

        wait_until(firefox.find_element_by_link_text, "LOG OUT")
        firefox.find_element_by_link_text("LOG OUT").click()

        extra_data = {"groups": ["tkdqmdoctor-shiftleaders"]}
        mixer.blend(SocialAccount, user=user, extra_data=extra_data)

        firefox.get("{}".format(live_server.url))
        wait_until(firefox.find_element_by_link_text, "Login")
        try_to_login_user(firefox, user.username, PASSWORD)

        wait_until(firefox.find_element_by_link_text, "Logout shifter1")
        user = User.objects.get(username="shifter1")

        assert user.is_staff
        assert not user.is_superuser
        assert not user.userprofile.is_shifter
        assert user.userprofile.is_shiftleader
        firefox.find_element_by_link_text("Logout shifter1").click()

        firefox.get("{}".format(live_server.url))
        try_to_login_user(firefox, superuser.username, PASSWORD)

        wait_until(firefox.find_element_by_link_text, "Admin Settings")
        firefox.find_element_by_link_text("Admin Settings").click()
        firefox.find_element_by_link_text("Social accounts").click()
        firefox.find_element_by_link_text("shifter1").click()
        extra_data_text_field = firefox.find_element_by_id("id_extra_data").text

        assert "tkdqmdoctor-shiftleaders" in extra_data_text_field

        firefox.find_element_by_link_text("Home").click()
        firefox.find_element_by_link_text("Users").click()
        firefox.find_element_by_link_text("shifter1").click()
        userprofile_text = firefox.find_element_by_id("userprofile-0").text

        assert "Guest" not in userprofile_text
        assert "Shifter" not in userprofile_text
        assert "Shift Leader" in userprofile_text
        assert "tkdqmdoctor-shiftleaders" in userprofile_text
