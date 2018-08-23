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

    def test_create_new_certification_when_no_checklist_exists(
            self, firefox, live_server, shifter, some_certified_runs, wait):
        firefox.get('%s' % live_server.url)
        try_to_login_user(firefox, SHIFTER1_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Add Run").click()
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
            self,
            website,
            shifter,
            legitimate_reference_runs,
            legitimate_types,
            some_checklists,
            wait):
        try_to_login_user(website, SHIFTER1_USERNAME, PASSWORD)
        wait_until(website.find_element_by_link_text, "Add Run")
        website.find_element_by_link_text("Add Run").click()
        check_all_checklists(website, wait)
        fill_and_submit_add_run_form(website)

        wait_for_cell(website, "456789")

        website.find_elements_by_class_name("edit_run")[1] \
            .find_element_by_tag_name("a").click()

        wait.until(EC.presence_of_element_located((By.ID, "id_run_number")))
        website.find_element_by_id("id_run_number").click()
        website.find_element_by_id("id_run_number").clear()
        website.find_element_by_id("id_run_number").send_keys("555789")

        website.find_element_by_id("id_submit_add_run").click()

        wait_for_cell(website, "555789")

    def test_incompatible_type(
            self,
            website,
            wait,
            shifter,
            legitimate_reference_runs,
            legitimate_types):
        try_to_login_user(website, SHIFTER1_USERNAME, PASSWORD)
        wait_until(website.find_element_by_link_text, "Add Run").click()

        wait_until(
            Select(website.find_element_by_id("id_type")).select_by_visible_text,
            "Express Cosmics 3.8 T Cosmics Cosmics "
            "/StreamExpressCosmics/Run2018D-Express-v1/DQMIO"
        )

        wait_until(website.find_element_by_id, "id_match_type").click()

        wait_until(
            Select(
                website.find_element_by_id("id_reference_run")).select_by_visible_text,
            "100 Express Collisions 3.8 T Proton-Proton 13 TeV "
            "/StreamExpress/Run2018A-Express-v1/DQMIO"
        )

        fill_form_with_data(website)
        website.find_element_by_id("id_submit_add_run").click()

        alert_text = website.find_element_by_class_name("alert").text
        assert "Reference run is incompatible selected Type" in alert_text

    def test_no_duplicate_certifications(
            self,
            website,
            wait,
            shifter,
            legitimate_reference_runs,
            legitimate_types):
        try_to_login_user(website, SHIFTER1_USERNAME, PASSWORD)
        wait_until(website.find_element_by_link_text, "Add Run").click()

        wait_until(
            Select(website.find_element_by_id("id_type")).select_by_visible_text,
            "Express Collisions 3.8 T Proton-Proton 13 TeV "
            "/StreamExpress/Run2018A-Express-v1/DQMIO"
        )

        wait_until(
            Select(
                website.find_element_by_id("id_reference_run")).select_by_visible_text,
            "100 Express Collisions 3.8 T Proton-Proton 13 TeV "
            "/StreamExpress/Run2018A-Express-v1/DQMIO"
        )

        fill_form_with_data(website)
        website.find_element_by_id("id_submit_add_run").click()

        wait_until(website.find_element_by_link_text, "Add Run").click()

        wait_until(
            Select(website.find_element_by_id("id_type")).select_by_visible_text,
            "Express Collisions 3.8 T Proton-Proton 13 TeV "
            "/StreamExpress/Run2018A-Express-v1/DQMIO"
        )

        wait_until(
            Select(
                website.find_element_by_id("id_reference_run")).select_by_visible_text,
            "101 Express Collisions 3.8 T Proton-Proton 13 TeV "
            "/StreamExpress/Run2018A-Express-v1/DQMIO"
        )

        fill_form_with_data(website)
        website.find_element_by_id("id_submit_add_run").click()

        alert_text = website.find_element_by_class_name("alert").text
        assert "This run (456789, Collisions Express) was already " \
               "certified by shifter1 on " in alert_text

        wait_until(
            Select(
                website.find_element_by_id("id_reference_run")).select_by_visible_text,
            "100 Express Collisions 3.8 T Proton-Proton 13 TeV "
            "/StreamExpress/Run2018A-Express-v1/DQMIO"
        )

        alert_text = website.find_element_by_class_name("alert").text
        assert "This run (456789, Collisions Express) was already " \
               "certified by shifter1 on " in alert_text

        website.find_element_by_id("id_run_number").clear()
        website.find_element_by_id("id_run_number").send_keys(2)
        website.find_element_by_id("id_submit_add_run").click()
        wait_until(website.find_element_by_link_text, "Add Run")
