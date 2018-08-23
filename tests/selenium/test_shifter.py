from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

from tests.credentials import *
from tests.utils.selenium_utilities import try_to_login_user, \
    check_all_checklists, fill_and_submit_add_run_form, fill_form_with_data
from tests.utils.wait import wait_until, wait_for_cell


class TestShifter:
    def test_can_create_type(self, firefox, live_server, shifter, wait):
        firefox.get('%s' % live_server.url)
        try_to_login_user(firefox, SHIFTER1_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Add Run").click()
        wait_until(firefox.find_element_by_id, "id_add_type").click()
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

    def test_can_check_checklists(self, firefox, live_server, shifter, some_checklists,
                                  wait):
        firefox.get('%s' % live_server.url)
        try_to_login_user(firefox, SHIFTER1_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Add Run").click()
        check_all_checklists(firefox, wait)

    def test_create_new_certification(
            self, firefox, live_server, shifter, some_certified_runs,
            some_checklists, wait):
        firefox.get('%s' % live_server.url)
        try_to_login_user(firefox, SHIFTER1_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Add Run").click()
        check_all_checklists(firefox, wait)
        fill_and_submit_add_run_form(firefox)

        wait_for_cell(firefox, "456789", MAX_WAIT=20)

    def test_create_new_certification_without_checking_checklist(
            self, firefox, live_server, shifter, some_certified_runs,
            some_checklists, wait):
        firefox.get('%s' % live_server.url)
        try_to_login_user(firefox, SHIFTER1_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Add Run").click()
        fill_and_submit_add_run_form(firefox)

        headline = firefox.find_element_by_tag_name("h1").text
        assert "Add new Run" in headline  # No Submit

    def test_generate_summary(self):
        pass

    def test_can_update_certification(
            self, firefox, live_server, shifter, some_certified_runs,
            some_checklists, wait):
        firefox.get('%s' % live_server.url)
        try_to_login_user(firefox, SHIFTER1_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Add Run")
        firefox.find_element_by_link_text("Add Run").click()
        check_all_checklists(firefox, wait)
        fill_and_submit_add_run_form(firefox)

        wait_for_cell(firefox, "456789")

        firefox.find_elements_by_class_name("edit_run")[1].find_element_by_tag_name(
            "a").click()

        wait.until(EC.presence_of_element_located((By.ID, "id_run_number")))
        firefox.find_element_by_id("id_run_number").click()
        firefox.find_element_by_id("id_run_number").clear()
        firefox.find_element_by_id("id_run_number").send_keys("555789")

        firefox.find_element_by_id("id_submit_add_run").click()

        wait_for_cell(firefox, "555789")
