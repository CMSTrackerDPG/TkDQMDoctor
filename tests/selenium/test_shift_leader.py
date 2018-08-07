from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.credentials import SHIFTLEADER_USERNAME, PASSWORD
from tests.utils.selenium_utilities import try_to_login_user, \
    add_some_reference_runs


class TestShiftLeader:
    def test_can_create_reference_runs(self, live_server, firefox, shiftleader):
        firefox.get('{}'.format(live_server.url))
        try_to_login_user(firefox, SHIFTLEADER_USERNAME, PASSWORD)
        add_some_reference_runs(firefox)
        firefox.find_element_by_partial_link_text("Logout").click()

    def test_can_create_checklists(self, live_server, firefox, shiftleader, wait):
        firefox.get('{}'.format(live_server.url))
        try_to_login_user(firefox, SHIFTLEADER_USERNAME, PASSWORD)
        firefox.find_element_by_link_text("Admin Settings").click()
        firefox.find_element_by_css_selector(
            "tr.model-checklist > td > a.addlink").click()
        firefox.find_element_by_id("id_title").clear()
        firefox.find_element_by_id("id_title").send_keys("Some Checklist")
        firefox.find_element_by_id("id_identifier").clear()
        firefox.find_element_by_id("id_identifier").send_keys("general")
        firefox.find_element_by_id("id_checklistitemgroup_set-0-name").clear()
        firefox.find_element_by_id("id_checklistitemgroup_set-0-name").send_keys(
            "First Item Group")
        firefox.find_element_by_name("_save").click()
        firefox.find_element_by_link_text("VIEW SITE").click()
        firefox.find_element_by_link_text("Add Run").click()
        wait.until(
            EC.presence_of_element_located(
                (By.ID, "id_checklist_general")
            )
        )

        labels = firefox.find_elements_by_tag_name('label')
        assert "Some Checklist Checklist [Show]" in [label.text for label in labels]

