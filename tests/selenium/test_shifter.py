from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

from tests.credentials import *
from tests.utils.selenium_utilities import try_to_login_user, \
    check_all_checklists, fill_and_submit_add_run_form, \
    wait_for_cell


class TestShifter:
    def test_can_create_type(self, firefox, live_server, shifter, wait):
        firefox.get('%s' % live_server.url)
        try_to_login_user(firefox, SHIFTER1_USERNAME, PASSWORD)
        firefox.find_element_by_link_text("Add Run").click()
        firefox.find_element_by_id("id_add_type").click()
        Select(firefox.find_element_by_id("id_reco")).select_by_visible_text("Express")
        Select(firefox.find_element_by_id("id_runtype")).select_by_visible_text(
            "Cosmics")
        Select(firefox.find_element_by_id("id_bfield")).select_by_visible_text("0 T")
        Select(firefox.find_element_by_id("id_beamtype")).select_by_visible_text(
            "Cosmics")
        Select(firefox.find_element_by_id("id_beamenergy")).select_by_visible_text(
            "Cosmics")
        firefox.find_element_by_id("id_dataset").clear()
        firefox.find_element_by_id("id_dataset").send_keys("/some/dataset")
        firefox.find_element_by_id("id_submit_type").click()

        # Make sure the newly created Type appears in the dropdown list
        wait.until(
            EC.text_to_be_present_in_element(
                (By.TAG_NAME, "select"),
                "Express Cosmics 0 T Cosmics Cosmics /some/dataset"
            )
        )

    def test_create_new_certification(
            self, firefox, live_server, shifter, some_certified_runs,
            some_checklists, wait):

        firefox.get('%s' % live_server.url)
        try_to_login_user(firefox, SHIFTER1_USERNAME, PASSWORD)
        firefox.find_element_by_link_text("Add Run").click()
        check_all_checklists(firefox, wait)
        fill_and_submit_add_run_form(firefox, wait)

        wait_for_cell(firefox, "456789", MAX_WAIT=20)

    def test_generate_summary(self):
        pass
