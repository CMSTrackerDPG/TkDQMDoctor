from django.urls import reverse
from selenium.webdriver.support.ui import Select

from tests.credentials import SUPERUSER_USERNAME, PASSWORD, SHIFTLEADER_USERNAME, \
    SHIFTER1_USERNAME, SHIFTER2_USERNAME


class TestLogin:
    def test_anonymous(self, live_server, firefox):
        firefox.get('%s%s' % (live_server.url, reverse('certhelper:list')))
        assert firefox.title == "TkDQMDoctor: List"
        assert "Login" in firefox.page_source
        assert "Admin Settings" not in firefox.page_source
        assert "Shift Leader" not in firefox.page_source
        assert "Shift Leader" not in firefox.page_source

    def test_login_superuser(self, live_server, firefox, superuser):
        firefox.get('%s%s' % (live_server.url, reverse('certhelper:list')))
        firefox.find_element_by_link_text("Login").click()
        firefox.find_element_by_id("id_login").clear()
        firefox.find_element_by_id("id_login").send_keys(SUPERUSER_USERNAME)
        firefox.find_element_by_id("id_password").clear()
        firefox.find_element_by_id("id_password").send_keys(PASSWORD)
        firefox.find_element_by_xpath("//button[@type='submit']").click()
        assert "Admin Settings" in firefox.page_source
        assert "Shift Leader" in firefox.page_source

    def test_login_shiftleader(self, live_server, firefox, shiftleader):
        firefox.get('%s%s' % (live_server.url, reverse('certhelper:list')))
        firefox.find_element_by_link_text("Login").click()
        firefox.find_element_by_id("id_login").clear()
        firefox.find_element_by_id("id_login").send_keys(SHIFTLEADER_USERNAME)
        firefox.find_element_by_id("id_password").clear()
        firefox.find_element_by_id("id_password").send_keys(PASSWORD)
        firefox.find_element_by_xpath("//button[@type='submit']").click()
        assert "Admin Settings" in firefox.page_source
        assert "Shift Leader" in firefox.page_source

    def test_login_shifter(self, live_server, firefox, shifter, second_shifter):
        firefox.get('%s%s' % (live_server.url, reverse('certhelper:list')))
        firefox.find_element_by_link_text("Login").click()
        firefox.find_element_by_id("id_login").clear()
        firefox.find_element_by_id("id_login").send_keys(SHIFTER1_USERNAME)
        firefox.find_element_by_id("id_password").clear()
        firefox.find_element_by_id("id_password").send_keys(PASSWORD)
        firefox.find_element_by_xpath("//button[@type='submit']").click()
        assert "Admin Settings" not in firefox.page_source
        assert "Shift Leader" not in firefox.page_source
        firefox.find_element_by_link_text("Logout {}".format(SHIFTER1_USERNAME)).click()

        firefox.get('%s%s' % (live_server.url, reverse('certhelper:list')))
        firefox.find_element_by_link_text("Login").click()
        firefox.find_element_by_id("id_login").clear()
        firefox.find_element_by_id("id_login").send_keys(SHIFTER2_USERNAME)
        firefox.find_element_by_id("id_password").clear()
        firefox.find_element_by_id("id_password").send_keys(PASSWORD)
        firefox.find_element_by_xpath("//button[@type='submit']").click()
        firefox.find_element_by_link_text("Logout {}".format(SHIFTER2_USERNAME)).click()

        assert "Admin Settings" not in firefox.page_source
        assert "Shift Leader" not in firefox.page_source


class TestCreateCertifications:
    def test_certification(self, live_server, firefox, shiftleader, shifter, second_shifter):
        firefox.get('%s%s' % (live_server.url, reverse('certhelper:list')))
        firefox.find_element_by_link_text("Login").click()
        firefox.find_element_by_id("id_login").clear()
        firefox.find_element_by_id("id_login").send_keys(SHIFTLEADER_USERNAME)
        firefox.find_element_by_id("id_password").clear()
        firefox.find_element_by_id("id_password").send_keys(PASSWORD)
        firefox.find_element_by_xpath("//button[@type='submit']").click()

        firefox.get('%s%s' % (live_server.url, "/admin/certhelper/referencerun/add/"))

        firefox.find_element_by_id("id_reference_run").clear()
        firefox.find_element_by_id("id_reference_run").send_keys("1")
        Select(firefox.find_element_by_id("id_reco")).select_by_visible_text("Express")
        Select(firefox.find_element_by_id("id_runtype")).select_by_visible_text("Cosmics")
        Select(firefox.find_element_by_id("id_bfield")).select_by_visible_text("0 T")
        Select(firefox.find_element_by_id("id_beamtype")).select_by_visible_text("Cosmics")
        Select(firefox.find_element_by_id("id_beamenergy")).select_by_visible_text("Cosmics")
        firefox.find_element_by_id("id_dataset").clear()
        firefox.find_element_by_id("id_dataset").send_keys("/some/dataset")
        firefox.find_element_by_name("_save").click()
        assert "Add reference run" in firefox.page_source
        firefox.find_element_by_link_text("Add reference run").click()
        firefox.find_element_by_id("id_reference_run").clear()
        firefox.find_element_by_id("id_reference_run").send_keys("2")
        Select(firefox.find_element_by_id("id_reco")).select_by_visible_text("Prompt")
        Select(firefox.find_element_by_id("id_runtype")).select_by_visible_text("Collisions")
        firefox.find_element_by_id("id_runtype").click()
        Select(firefox.find_element_by_id("id_bfield")).select_by_visible_text("3.8 T")
        firefox.find_element_by_id("id_bfield").click()
        Select(firefox.find_element_by_id("id_beamtype")).select_by_visible_text("Proton-Proton")
        firefox.find_element_by_id("id_beamtype").click()
        Select(firefox.find_element_by_id("id_beamenergy")).select_by_visible_text("13 TeV")
        firefox.find_element_by_id("id_beamenergy").click()
        firefox.find_element_by_id("id_dataset").click()
        firefox.find_element_by_id("id_dataset").clear()
        firefox.find_element_by_id("id_dataset").send_keys("/bla/blubb")
        firefox.find_element_by_name("_save").click()
        firefox.find_element_by_link_text("Log out").click()

        firefox.get('%s%s' % (live_server.url, reverse('certhelper:list')))
        firefox.find_element_by_link_text("Login").click()
        firefox.find_element_by_id("id_login").clear()
        firefox.find_element_by_id("id_login").send_keys(SHIFTER1_USERNAME)
        firefox.find_element_by_id("id_password").clear()
        firefox.find_element_by_id("id_password").send_keys(PASSWORD)
        firefox.find_element_by_xpath("//button[@type='submit']").click()

        firefox.find_element_by_link_text("Add Run").click()
        firefox.find_element_by_id("id_type").click()
        firefox.find_element_by_xpath("//button[@type='button']").click()
        Select(firefox.find_element_by_id("id_reco")).select_by_visible_text("Express")
        firefox.find_element_by_id("id_reco").click()
        Select(firefox.find_element_by_id("id_runtype")).select_by_visible_text("Cosmics")
        firefox.find_element_by_id("id_runtype").click()
        Select(firefox.find_element_by_id("id_bfield")).select_by_visible_text("0 T")
        firefox.find_element_by_id("id_bfield").click()
        Select(firefox.find_element_by_id("id_beamtype")).select_by_visible_text("Cosmics")
        firefox.find_element_by_id("id_beamtype").click()
        Select(firefox.find_element_by_id("id_beamenergy")).select_by_visible_text("13 TeV")
        firefox.find_element_by_id("id_beamenergy").click()
        firefox.find_element_by_id("id_dataset").click()
        firefox.find_element_by_id("id_dataset").clear()
        firefox.find_element_by_id("id_dataset").send_keys("/blabla/set")
        firefox.find_element_by_xpath("//button[@type='submit']").click()
        Select(firefox.find_element_by_id("id_type")).select_by_visible_text(
            "Express Cosmics 0 T Cosmics 13 TeV /blabla/set")
        firefox.find_element_by_id("id_type").click()
        Select(firefox.find_element_by_id("id_reference_run")).select_by_visible_text(
            "1 Express Cosmics 0 T Cosmics Cosmics /some/dataset")
        firefox.find_element_by_id("id_reference_run").click()
        firefox.find_element_by_id("id_run_number").click()
        firefox.find_element_by_id("id_run_number").clear()
        firefox.find_element_by_id("id_run_number").send_keys("1")
        Select(firefox.find_element_by_id("id_trackermap")).select_by_visible_text("Exists")
        firefox.find_element_by_id("id_trackermap").click()
        firefox.find_element_by_id("id_number_of_ls").click()
        firefox.find_element_by_id("id_number_of_ls").clear()
        firefox.find_element_by_id("id_number_of_ls").send_keys("1")
        firefox.find_element_by_id("id_int_luminosity").clear()
        firefox.find_element_by_id("id_int_luminosity").send_keys("0")
        Select(firefox.find_element_by_id("id_pixel")).select_by_visible_text("Good")
        Select(firefox.find_element_by_id("id_sistrip")).select_by_visible_text("Good")
        Select(firefox.find_element_by_id("id_tracking")).select_by_visible_text("Good")
        firefox.find_element_by_xpath("//button[@type='submit']").click()
        firefox.find_element_by_link_text("Add Run").click()
        firefox.find_element_by_xpath("//button[@type='button']").click()
        Select(firefox.find_element_by_id("id_reco")).select_by_visible_text("Prompt")
        firefox.find_element_by_id("id_reco").click()
        Select(firefox.find_element_by_id("id_runtype")).select_by_visible_text("Collisions")
        firefox.find_element_by_id("id_runtype").click()
        Select(firefox.find_element_by_id("id_bfield")).select_by_visible_text("3.8 T")
        firefox.find_element_by_id("id_bfield").click()
        Select(firefox.find_element_by_id("id_beamtype")).select_by_visible_text("Proton-Proton")
        firefox.find_element_by_id("id_beamtype").click()
        Select(firefox.find_element_by_id("id_beamenergy")).select_by_visible_text("13 TeV")
        firefox.find_element_by_id("id_beamenergy").click()
        firefox.find_element_by_id("id_dataset").click()
        firefox.find_element_by_id("id_dataset").clear()
        firefox.find_element_by_id("id_dataset").send_keys("/another/dataset")
        firefox.find_element_by_xpath("//button[@type='submit']").click()
        Select(firefox.find_element_by_id("id_type")).select_by_visible_text(
            "Prompt Collisions 3.8 T Proton-Proton 13 TeV /another/dataset")
        firefox.find_element_by_id("id_type").click()
        Select(firefox.find_element_by_id("id_reference_run")).select_by_visible_text(
            "2 Prompt Collisions 3.8 T Proton-Proton 13 TeV /bla/blubb")
        firefox.find_element_by_id("id_reference_run").click()
        firefox.find_element_by_id("id_run_number").click()
        firefox.find_element_by_id("id_run_number").clear()
        firefox.find_element_by_id("id_run_number").send_keys("2")
        Select(firefox.find_element_by_id("id_trackermap")).select_by_visible_text("Exists")
        firefox.find_element_by_id("id_trackermap").click()
        firefox.find_element_by_id("id_number_of_ls").click()
        firefox.find_element_by_id("id_number_of_ls").clear()
        firefox.find_element_by_id("id_number_of_ls").send_keys("1")
        firefox.find_element_by_id("id_int_luminosity").click()
        firefox.find_element_by_id("id_int_luminosity").clear()
        firefox.find_element_by_id("id_int_luminosity").send_keys("1")
        Select(firefox.find_element_by_id("id_pixel")).select_by_visible_text("Good")
        Select(firefox.find_element_by_id("id_sistrip")).select_by_visible_text("Good")
        Select(firefox.find_element_by_id("id_tracking")).select_by_visible_text("Good")
        firefox.find_element_by_xpath("//button[@type='submit']").click()

        # generate summary
        firefox.find_element_by_link_text("Generate Summary").click()
        firefox.find_element_by_link_text("Back to list of runs").click()

        # logout user2
        firefox.find_element_by_link_text("Logout {}".format(SHIFTER1_USERNAME)).click()
        firefox.get('%s%s' % (live_server.url, reverse('certhelper:list')))

        # Login shifter2
        firefox.find_element_by_link_text("Login").click()
        firefox.find_element_by_id("id_login").clear()
        firefox.find_element_by_id("id_login").send_keys(SHIFTER2_USERNAME)
        firefox.find_element_by_id("id_password").clear()
        firefox.find_element_by_id("id_password").send_keys(PASSWORD)
        firefox.find_element_by_xpath("//button[@type='submit']").click()

        firefox.find_element_by_link_text("Add Run").click()
        Select(firefox.find_element_by_id("id_type")).select_by_visible_text(
            "Express Cosmics 0 T Cosmics 13 TeV /blabla/set")
        firefox.find_element_by_id("id_type").click()
        Select(firefox.find_element_by_id("id_reference_run")).select_by_visible_text(
            "1 Express Cosmics 0 T Cosmics Cosmics /some/dataset")
        firefox.find_element_by_id("id_reference_run").click()
        firefox.find_element_by_id("id_run_number").click()
        firefox.find_element_by_id("id_run_number").clear()
        firefox.find_element_by_id("id_run_number").send_keys("1")
        Select(firefox.find_element_by_id("id_trackermap")).select_by_visible_text("Exists")
        firefox.find_element_by_id("id_number_of_ls").clear()
        firefox.find_element_by_id("id_number_of_ls").send_keys("0")
        firefox.find_element_by_id("id_int_luminosity").clear()
        firefox.find_element_by_id("id_int_luminosity").send_keys("0")
        Select(firefox.find_element_by_id("id_pixel")).select_by_visible_text("Good")
        Select(firefox.find_element_by_id("id_sistrip")).select_by_visible_text("Good")
        Select(firefox.find_element_by_id("id_tracking")).select_by_visible_text("Good")
        firefox.find_element_by_xpath("//div[@id='content']/form/div/button/span").click()

        assert "already certified by shifter1" in firefox.page_source

        firefox.find_element_by_id("id_run_number").clear()
        firefox.find_element_by_id("id_run_number").send_keys("3")
        firefox.find_element_by_xpath("//button[@type='submit']").click()

        # Logout shifter2
        firefox.find_element_by_link_text("Logout {}".format(SHIFTER2_USERNAME)).click()
        firefox.get('%s%s' % (live_server.url, reverse('certhelper:list')))

        # Login shiftleader
        firefox.get('%s%s' % (live_server.url, reverse('certhelper:list')))
        firefox.find_element_by_link_text("Login").click()
        firefox.find_element_by_id("id_login").clear()
        firefox.find_element_by_id("id_login").send_keys(SHIFTLEADER_USERNAME)
        firefox.find_element_by_id("id_password").clear()
        firefox.find_element_by_id("id_password").send_keys(PASSWORD)
        firefox.find_element_by_xpath("//button[@type='submit']").click()

        # Go to Shift leader report
        firefox.find_element_by_link_text("Shift Leader").click()
        firefox.find_element_by_link_text("Certified Runs").click()
        firefox.find_element_by_xpath("//div[@id='runtable']/div/table/tbody/tr/td[13]/div/a/span").click()
        firefox.find_element_by_id("id_run_number").clear()
        firefox.find_element_by_id("id_run_number").send_keys("1")
        firefox.find_element_by_xpath("//div[@id='content']/form/div/button/span").click()
        firefox.find_element_by_id("id_run_number").clear()
        firefox.find_element_by_id("id_run_number").send_keys("3")
        firefox.find_element_by_xpath("//button[@type='submit']").click()
        firefox.find_element_by_link_text("Shift Leader").click()
        firefox.find_element_by_link_text("Certified Runs").click()
        firefox.find_element_by_xpath("//div[@id='runtable']/div/table/tbody/tr/td[13]/div/a/span").click()
        firefox.find_element_by_id("id_run_number").clear()
        firefox.find_element_by_id("id_run_number").send_keys("4")
        Select(firefox.find_element_by_id("id_tracking")).select_by_visible_text("Bad")
        firefox.find_element_by_id("id_tracking").click()
        firefox.find_element_by_xpath("//div[@id='content']/form/div/button/span").click()
        firefox.find_element_by_link_text("Shift Leader").click()

        assert "Collisions: <strong>0</strong> in Stream-Express (<strong>0 pb<sup>-1</sup></strong>), " \
               "<strong>1</strong> in Prompt-Reco (<strong>1.0 pb<sup>-1</sup></strong>)" in firefox.page_source
        assert "Stream-Express: total number=<strong>2</strong>" in firefox.page_source
        assert "BAD runs: total number=<strong>1</strong>" in firefox.page_source
