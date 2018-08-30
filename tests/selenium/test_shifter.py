import time

import pytest
from django.utils import timezone
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

from tests.credentials import *
from tests.utils.selenium_utilities import try_to_login_user, \
    check_all_checklists, fill_and_submit_add_run_form, fill_form_with_data, \
    select_types_and_reference_runs_in_form
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

        wait_until(firefox.find_element_by_id, "id_submit_add_run")

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

        wait_until(firefox.find_element_by_link_text, "Add Run")
        wait_for_cell(firefox, "456789", MAX_WAIT=60)

    def test_create_new_certification_when_no_checklist_exists(
            self, firefox, live_server, shifter, some_certified_runs, wait):
        firefox.get('%s' % live_server.url)
        try_to_login_user(firefox, SHIFTER1_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Add Run").click()
        fill_and_submit_add_run_form(firefox)

        wait_until(firefox.find_element_by_link_text, "Add Run")
        wait_for_cell(firefox, "456789", MAX_WAIT=60)

    def test_create_new_certification_without_checking_checklist(
            self, firefox, live_server, shifter, some_certified_runs,
            some_checklists, wait):
        firefox.get('%s' % live_server.url)
        try_to_login_user(firefox, SHIFTER1_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Add Run").click()
        fill_and_submit_add_run_form(firefox)
        wait_until(firefox.find_element_by_id, "id_submit_add_run")  # no submit

        headline = firefox.find_element_by_tag_name("h1").text
        assert "Add new Run" in headline  # No submit happened

    def test_generate_summary(self, website, shifter, runs_for_summary_report):
        try_to_login_user(website, SHIFTER1_USERNAME, PASSWORD)
        wait_until(website.find_element_by_link_text, "Add Run")
        website.find_element_by_link_text("Generate Summary").click()
        info_text = website.find_element_by_class_name("alert-info").text

        assert "Applied filters:" in info_text
        today = timezone.now().strftime("%Y-%m-%d")
        assert "Date: {}".format(today) in info_text

        summary = website.find_element_by_id("summary")

        assert "=============Reference Runs===============" in summary.text
        assert "300250 Prompt Cosmics 3.8 T Cosmics Cosmics /Cosmics/Run2018D-PromptReco-v2/DQMIO" in summary.text
        assert "300200 Express Cosmics 3.8 T Cosmics Cosmics /StreamExpressCosmics/Run2018D-Express-v1/DQMIO" in summary.text
        assert "300150 Prompt Collisions 3.8 T Proton-Proton 13 TeV /ZeroBias/Run2018D-PromptReco-v2/DQMIO" in summary.text
        assert "300101 Express Collisions 3.8 T Proton-Proton 13 TeV /StreamExpress/Run2018A-Express-v1/DQMIO" in summary.text

        assert "=============Tracker Maps=================" in summary.text
        assert "Type 1" in summary.text
        assert "Missing: 300003 300004 300021" in summary.text
        assert "Exists: 300009 300023" in summary.text

        assert "Type 2" in summary.text
        assert "Missing: 300006 300013 300015 300019 300022" in summary.text
        assert "Exists: 300001 300002 300014 300016 300020" in summary.text

        assert "Type 3" in summary.text
        assert "Missing: 300003 300004 300021" in summary.text
        assert "Exists: 300009 300023" in summary.text

        assert "Type 4" in summary.text
        assert "Missing: 300007 300008 300017 300024" in summary.text
        assert "Exists: 300000 300012" in summary.text

        assert "=============Certified Runs===============" in summary.text

        assert "Type 1" in summary.text
        assert "Bad: 300001 300005 300010 300011 300018" in summary.text

        assert "Type 2" in summary.text
        assert "Bad: 300001 300002 300006 300013 300014 300016 300019 300020 300022" in summary.text
        assert "Good: 300015" in summary.text

        assert "Type 3" in summary.text
        assert "Good: 300003 300009" in summary.text
        assert "Bad: 300004 300021 300023" in summary.text

        assert "Type 4" in summary.text
        assert "Bad: 300000 300008 300012 300017 300024" in summary.text
        assert "Good: 300007" in summary.text

        assert """
=============Sum of Quantities============
+--------+-----------+------------------------+
| Type 1 | Sum of LS | Sum of int. luminosity |
+--------+-----------+------------------------+
| Bad    | 3424      | 3534                   |
+--------+-----------+------------------------+""" in summary.text

        assert "| Type 2 | Sum of LS | Sum of int. luminosity |" in summary.text
        assert "| Bad    | 4487      | 5316                   |" in summary.text
        assert "| Good   | 265       | 432                    |" in summary.text

        assert "| Type 3 | Sum of LS | Sum of int. luminosity |" in summary.text
        assert "| Good   | 708       | 0                      " in summary.text
        assert "| Bad    | 1015      | 0                      |" in summary.text

        assert "| Type 4 | Sum of LS | Sum of int. luminosity |" in summary.text
        assert "| Bad    | 2091      | 0                      |" in summary.text
        assert "| Good   | 341       | 0                      |" in summary.text

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

        wait_until(website.find_element_by_link_text, "Add Run")
        wait_for_cell(website, "456789", MAX_WAIT=60)

        website.find_elements_by_class_name("edit_run")[1] \
            .find_element_by_tag_name("a").click()

        wait.until(EC.presence_of_element_located((By.ID, "id_run_number")))
        website.find_element_by_id("id_run_number").click()
        website.find_element_by_id("id_run_number").clear()
        website.find_element_by_id("id_run_number").send_keys("555789")

        website.find_element_by_id("id_submit_add_run").click()

        wait_until(website.find_element_by_link_text, "Add Run")
        wait_for_cell(website, "555789", MAX_WAIT=60)

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
            "300100 Express Collisions 3.8 T Proton-Proton 13 TeV "
            "/StreamExpress/Run2018A-Express-v1/DQMIO"
        )

        fill_form_with_data(website)
        website.find_element_by_id("id_submit_add_run").click()
        alert_text = wait_until(website.find_element_by_class_name, "alert").text
        assert "Reference run is incompatible with selected Type" in alert_text

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
            "300100 Express Collisions 3.8 T Proton-Proton 13 TeV "
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
            "300101 Express Collisions 3.8 T Proton-Proton 13 TeV "
            "/StreamExpress/Run2018A-Express-v1/DQMIO"
        )

        fill_form_with_data(website)
        website.find_element_by_id("id_submit_add_run").click()

        alert_text = wait_until(website.find_element_by_class_name, "alert").text
        assert "This run (456789, Collisions Express) was already " \
               "certified by shifter1 on " in alert_text

        wait_until(
            Select(
                website.find_element_by_id("id_reference_run")).select_by_visible_text,
            "300100 Express Collisions 3.8 T Proton-Proton 13 TeV "
            "/StreamExpress/Run2018A-Express-v1/DQMIO"
        )

        alert_text = website.find_element_by_class_name("alert").text
        assert "This run (456789, Collisions Express) was already " \
               "certified by shifter1 on " in alert_text

        website.find_element_by_id("id_run_number").clear()
        website.find_element_by_id("id_run_number").send_keys(2)
        website.find_element_by_id("id_submit_add_run").click()
        wait_until(website.find_element_by_link_text, "Add Run")

    def test_run_number_validation(
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
            "300100 Express Collisions 3.8 T Proton-Proton 13 TeV "
            "/StreamExpress/Run2018A-Express-v1/DQMIO"
        )

        with pytest.raises(NoSuchElementException):
            website.find_element_by_class_name("has-error")
        with pytest.raises(NoSuchElementException):
            website.find_element_by_class_name("has-warning")
        with pytest.raises(NoSuchElementException):
            website.find_element_by_class_name("has-success")

        website.find_element_by_id("id_run_number").clear()
        website.find_element_by_id("id_run_number").send_keys("299999")

        with pytest.raises(NoSuchElementException):
            website.find_element_by_class_name("has-warning")
        with pytest.raises(NoSuchElementException):
            website.find_element_by_class_name("has-success")

        help_text = wait_until(website.find_element_by_class_name, "has-error") \
            .find_element_by_class_name("help-block").text
        assert "Run number is too low" in help_text
        website.find_element_by_id("id_run_number").clear()
        website.find_element_by_id("id_run_number").send_keys("1000000")

        with pytest.raises(NoSuchElementException):
            website.find_element_by_class_name("has-warning")
        with pytest.raises(NoSuchElementException):
            website.find_element_by_class_name("has-success")

        help_text = wait_until(website.find_element_by_class_name, "has-error") \
            .find_element_by_class_name("help-block").text
        assert "Run number is too high" in help_text

        with pytest.raises(NoSuchElementException):
            website.find_element_by_class_name("has-warning")
        with pytest.raises(NoSuchElementException):
            website.find_element_by_class_name("has-success")

        website.find_element_by_id("id_run_number").clear()
        website.find_element_by_id("id_run_number").send_keys("306101")

        with pytest.raises(NoSuchElementException):
            website.find_element_by_class_name("has-error")
        with pytest.raises(NoSuchElementException):
            website.find_element_by_class_name("has-success")

        help_text = wait_until(website.find_element_by_class_name, "has-warning") \
            .find_element_by_class_name("help-block").text
        assert "Run number seems odd" in help_text

        website.find_element_by_id("id_run_number").clear()
        website.find_element_by_id("id_run_number").send_keys("306100")

        with pytest.raises(NoSuchElementException):
            website.find_element_by_class_name("has-error")
        with pytest.raises(NoSuchElementException):
            website.find_element_by_class_name("has-warning")

        help_text = wait_until(website.find_element_by_class_name, "has-success") \
            .find_element_by_class_name("help-block").text
        assert "" == help_text

    def test_cosmics_int_luminosity_validation(
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

        wait_until(
            Select(
                website.find_element_by_id("id_reference_run")).select_by_visible_text,
            "300200 Express Cosmics 3.8 T Cosmics Cosmics "
            "/StreamExpressCosmics/Run2018D-Express-v1/DQMIO"
        )

        website.find_element_by_id("id_int_luminosity").clear()
        website.find_element_by_id("id_int_luminosity").send_keys("1")

        with pytest.raises(NoSuchElementException):
            website.find_element_by_class_name("has-error")
        with pytest.raises(NoSuchElementException):
            website.find_element_by_class_name("has-success")

        help_text = wait_until(website.find_element_by_class_name, "has-warning") \
            .find_element_by_class_name("help-block").text
        assert "You certify a cosmics run. Are you sure about this value?" in help_text

        website.find_element_by_id("id_int_luminosity").clear()
        website.find_element_by_id("id_int_luminosity").send_keys("0")

        with pytest.raises(NoSuchElementException):
            website.find_element_by_class_name("has-warning")
        with pytest.raises(NoSuchElementException):
            website.find_element_by_class_name("has-error")

        help_text = wait_until(website.find_element_by_class_name, "has-success") \
            .find_element_by_class_name("help-block").text
        assert "" == help_text

    def test_collisions_int_luminosity_validation(
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
            "300100 Express Collisions 3.8 T Proton-Proton 13 TeV "
            "/StreamExpress/Run2018A-Express-v1/DQMIO"
        )

        website.find_element_by_id("id_int_luminosity").clear()
        website.find_element_by_id("id_int_luminosity").send_keys("1")

        with pytest.raises(NoSuchElementException):
            website.find_element_by_class_name("has-error")
        with pytest.raises(NoSuchElementException):
            website.find_element_by_class_name("has-warning")

        help_text = wait_until(website.find_element_by_class_name, "has-success") \
            .find_element_by_class_name("help-block").text
        assert "" == help_text

    def test_create_certification_lowstat(
            self, website, shifter, some_certified_runs, wait):
        try_to_login_user(website, SHIFTER1_USERNAME, PASSWORD)
        wait_until(website.find_element_by_link_text, "Add Run").click()
        select_types_and_reference_runs_in_form(website)
        website.find_element_by_id("id_pixel_lowstat").click()
        website.find_element_by_id("id_sistrip_lowstat").click()
        website.find_element_by_id("id_tracking_lowstat").click()
        fill_form_with_data(website, {"pixel": "Bad", "sistrip": "Good", "tracking": "Excluded"})
        website.find_element_by_id("id_submit_add_run").click()
        wait_for_cell(website, "456789", MAX_WAIT=60)

        pixel = website.find_element_by_css_selector("td.pixel").get_attribute('innerHTML')
        sistrip = website.find_element_by_css_selector("td.sistrip").get_attribute('innerHTML')
        tracking = website.find_element_by_css_selector("td.tracking").get_attribute('innerHTML')

        assert "bad-component" in pixel
        assert "Lowstat" in pixel
        assert "good-component" in sistrip
        assert "Lowstat" in sistrip
        assert "excluded-component" in tracking
        assert "Excluded" in tracking

        website.find_elements_by_class_name("edit_run")[1] \
            .find_element_by_tag_name("a").click()

        assert website.find_element_by_id("id_pixel_lowstat").is_selected()
        assert website.find_element_by_id("id_sistrip_lowstat").is_selected()
        assert not website.find_element_by_id("id_tracking_lowstat").is_selected()

        website.find_element_by_id("id_pixel_lowstat").click()
        website.find_element_by_id("id_sistrip_lowstat").click()

        website.find_element_by_id("id_submit_add_run").click()
        wait_for_cell(website, "456789", MAX_WAIT=60)

        pixel = website.find_element_by_css_selector("td.pixel").get_attribute('innerHTML')
        sistrip = website.find_element_by_css_selector("td.sistrip").get_attribute('innerHTML')
        tracking = website.find_element_by_css_selector("td.tracking").get_attribute('innerHTML')

        assert "bad-component" in pixel
        assert "Bad" in pixel
        assert "Lowstat" not in pixel
        assert "good-component" in sistrip
        assert "Good" in sistrip
        assert "Lowstat" not in pixel
        assert "excluded-component" in tracking
        assert "Excluded" in tracking

