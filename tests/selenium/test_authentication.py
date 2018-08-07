from tests.credentials import *
from tests.utils.selenium_utilities import try_to_login_user


class TestAuthentication:
    def test_anonymous(self, live_server, firefox):
        firefox.get('{}'.format(live_server.url))
        assert firefox.title == "TkDQMDoctor: List"
        assert "Login" in firefox.page_source
        assert "Admin Settings" not in firefox.page_source
        assert "Shift Leader" not in firefox.page_source

    def test_login_superuser(self, live_server, firefox, superuser):
        firefox.get('{}'.format(live_server.url))
        try_to_login_user(firefox, SUPERUSER_USERNAME, PASSWORD)
        assert "Admin Settings" in firefox.page_source
        assert "Shift Leader" in firefox.page_source

    def test_login_shiftleader(self, live_server, firefox, shiftleader):
        firefox.get('{}'.format(live_server.url))
        try_to_login_user(firefox, SHIFTLEADER_USERNAME, PASSWORD)
        assert "Admin Settings" in firefox.page_source
        assert "Shift Leader" in firefox.page_source

    def test_login_shifter(self, live_server, firefox, shifter, second_shifter):
        firefox.get('{}'.format(live_server.url))
        try_to_login_user(firefox, SHIFTER1_USERNAME, PASSWORD)
        assert "Admin Settings" not in firefox.page_source
        assert "Shift Leader" not in firefox.page_source
        firefox.find_element_by_link_text("Logout {}".format(SHIFTER1_USERNAME)).click()

        firefox.get('{}'.format(live_server.url))
        try_to_login_user(firefox, SHIFTER2_USERNAME, PASSWORD)
        firefox.find_element_by_link_text("Logout {}".format(SHIFTER2_USERNAME)).click()

        assert "Admin Settings" not in firefox.page_source
        assert "Shift Leader" not in firefox.page_source
