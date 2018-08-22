import time

import pytest
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.credentials import SHIFTLEADER_USERNAME, PASSWORD, ADMIN_USERNAME
from tests.utils.selenium_utilities import try_to_login_user, \
    add_some_reference_runs, set_shift_leader_filter_date
from tests.utils.utilities import create_recent_run, create_runs
from tests.utils.wait import wait_for_cell, wait_until


class TestShiftLeader:
    def test_can_create_reference_runs(self, live_server, firefox, shiftleader):
        firefox.get('{}'.format(live_server.url))
        try_to_login_user(firefox, SHIFTLEADER_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Admin Settings")
        add_some_reference_runs(firefox)
        firefox.find_element_by_partial_link_text("Logout").click()

    def test_can_create_checklists(self, live_server, firefox, shiftleader, wait):
        firefox.get('{}'.format(live_server.url))
        try_to_login_user(firefox, SHIFTLEADER_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Admin Settings")
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
        wait_until(firefox.find_element_by_link_text, "Add Run")
        firefox.find_element_by_link_text("Add Run").click()
        wait.until(
            EC.presence_of_element_located(
                (By.ID, "id_checklist_general")
            )
        )

        labels = firefox.find_elements_by_tag_name('label')
        assert "Some Checklist Checklist [Show]" in [label.text for label in labels]

    def test_can_go_to_shift_leader_page(self, live_server, firefox, shiftleader, wait):
        firefox.get('{}'.format(live_server.url))
        try_to_login_user(firefox, SHIFTLEADER_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Shift Leader")
        firefox.find_element_by_link_text("Shift Leader").click()
        wait_until(firefox.find_element_by_link_text, "List of Certified Runs")
        assert "Shift Leader View" == firefox.find_element_by_tag_name("h1").text

    def test_delete_certification(self, live_server, firefox, shiftleader, wait):
        create_recent_run("123555")
        firefox.get('{}'.format(live_server.url))
        try_to_login_user(firefox, SHIFTLEADER_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Shift Leader")
        firefox.find_element_by_link_text("Shift Leader").click()
        wait_until(firefox.find_element_by_link_text, "Deleted Certifications")
        firefox.find_element_by_link_text("Deleted Certifications").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "delete_forever")))
        deleted_table = firefox.find_element_by_css_selector(
            "div#deleted-runs > div.table-container > table")
        assert "123555" not in deleted_table.text

        firefox.find_element_by_link_text("Certified Runs").click()
        wait_for_cell(firefox, "123555")

        table = firefox.find_element_by_css_selector(
            "div#runtable > div.table-container > table")
        assert "123555" in table.text
        firefox.find_elements_by_class_name("delete_run")[1] \
            .find_element_by_tag_name("a") \
            .click()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input + button")))
        firefox.find_element_by_css_selector("input + button ").click()
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div#deleted-runs > div.table-container > table")))
        table = firefox.find_element_by_css_selector(
            "div#runtable > div.table-container > table")
        assert "123555" not in table.text

        firefox.find_element_by_link_text("Deleted Certifications").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "delete_forever")))
        deleted_table = firefox.find_element_by_css_selector(
            "div#deleted-runs > div.table-container > table")
        assert "123555" in deleted_table.text

    def test_can_view_weekly_certification(self, live_server, firefox, shiftleader,
                                           wait):
        firefox.get('{}'.format(live_server.url))
        try_to_login_user(firefox, SHIFTLEADER_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Shift Leader")
        firefox.find_element_by_link_text("Shift Leader").click()
        wait.until(EC.presence_of_element_located((By.ID, "slr-weekly-cert")))
        weekly_report = firefox.find_element_by_id("slr-weekly-cert").text

        assert "Weekly Certification" in weekly_report
        assert "Prompt-Reco: total number=" in weekly_report

    def test_shift_leader_report_weekly(self, live_server, firefox, shiftleader,
                                        wait, runs_for_slr):
        firefox.get('{}'.format(live_server.url))
        try_to_login_user(firefox, SHIFTLEADER_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Shift Leader")
        firefox.find_element_by_link_text("Shift Leader").click()

        set_shift_leader_filter_date(firefox, "2018", "May", "14", "2018", "May", "20")

        wait.until(EC.presence_of_element_located((By.ID, "slr-weekly-cert")))
        weekly_report = firefox.find_element_by_id("slr-weekly-cert").text

        assert "Collisions:" in weekly_report
        assert "Prompt-Reco: total number=3, Integrated lumi=123133.55 pb⁻¹" in weekly_report
        assert "BAD runs: total number=3, Integrated lumi=123133.55 pb⁻¹" in weekly_report
        assert "Stream-Express: total number=8, Integrated lumi=161301.36 pb⁻¹" in weekly_report
        assert "BAD runs: total number=0, Integrated lumi=0 pb⁻¹" in weekly_report

        assert "Cosmics:" in weekly_report
        assert "Prompt-Reco: total number=1" in weekly_report
        assert "BAD runs: total number=1" in weekly_report
        assert "Stream-Express: total number=7" in weekly_report
        assert "BAD runs: total number=2" in weekly_report

    def test_shift_leader_report_day_by_day(self, live_server, firefox, shiftleader,
                                            wait, runs_for_slr):
        firefox.get('{}'.format(live_server.url))
        try_to_login_user(firefox, SHIFTLEADER_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Shift Leader")
        firefox.find_element_by_link_text("Shift Leader").click()

        set_shift_leader_filter_date(firefox, "2018", "May", "14", "2018", "May", "20")

        wait.until(EC.presence_of_element_located((By.ID, "slr-weekly-cert")))

        firefox.find_element_by_link_text("Day by day").click()
        firefox.find_element_by_link_text("Monday (2018-05-14)").click()
        wait.until(EC.presence_of_element_located((By.ID, "slr-2018-05-14")))
        day_report = firefox.find_element_by_id("slr-2018-05-14").text

        assert "Collisions: 3 in Stream-Express (5212.0 pb⁻¹)" in day_report
        assert ", 1 in Prompt-Reco (1.23 pb⁻¹)" in day_report
        assert "Cosmics: 3 in Stream Express, 1 in Prompt Reco" in day_report
        assert "Total number of BAD runs = 3 (1.23 pb⁻¹)" in day_report
        assert "Number of changed flags from Express to Prompt=0" in day_report

    def test_shift_leader_report_list_of_run_numbers(self, live_server, firefox,
                                                     shiftleader, wait):
        create_runs(2, 1, "Collisions", "Express", good=True, date="2018-05-14")
        create_runs(2, 6, "Collisions", "Express", good=False, date="2018-05-14")
        create_runs(2, 10, "Collisions", "Prompt", good=True, date="2018-05-15")
        create_runs(2, 15, "Collisions", "Prompt", good=False, date="2018-05-15")
        create_runs(2, 21, "Cosmics", "Express", good=True, date="2018-05-14")
        create_runs(2, 26, "Cosmics", "Express", good=False, date="2018-05-16")
        create_runs(2, 30, "Cosmics", "Prompt", good=True, date="2018-05-14")
        create_runs(2, 35, "Cosmics", "Prompt", good=False, date="2018-05-14")

        firefox.get('{}'.format(live_server.url))
        try_to_login_user(firefox, SHIFTLEADER_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Shift Leader")
        firefox.find_element_by_link_text("Shift Leader").click()

        set_shift_leader_filter_date(firefox, "2018", "May", "14", "2018", "May", "20")

        wait.until(EC.presence_of_element_located((By.ID, "slr-weekly-cert")))

        firefox.find_element_by_link_text("List of runs").click()
        firefox.find_element_by_link_text("All days").click()

        wait.until(EC.presence_of_element_located((By.ID, "slr-list-of-runs-all")))

        list_of_runs_div = firefox.find_element_by_id("slr-list-of-runs-all").text

        assert "List of runs certified StreamExpress" in list_of_runs_div
        assert "Collisions" in list_of_runs_div
        assert "Monday: 1, 2, 6, 7" in list_of_runs_div
        assert "Cosmics" in list_of_runs_div
        assert "Monday: 21, 22" in list_of_runs_div
        assert "Wednesday: 26, 27" in list_of_runs_div
        assert "List of runs certified Prompt" in list_of_runs_div
        assert "Collisions" in list_of_runs_div
        assert "Tuesday: 10, 11, 15, 16" in list_of_runs_div
        assert "Cosmics" in list_of_runs_div
        assert "Monday: 30, 31, 35, 36" in list_of_runs_div

    def test_shift_leader_checklist(self, live_server, firefox, shiftleader, wait,
                                    shiftleader_checklist):
        firefox.get('{}'.format(live_server.url))
        try_to_login_user(firefox, SHIFTLEADER_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Shift Leader")
        firefox.find_element_by_link_text("Shift Leader").click()
        wait.until(EC.presence_of_element_located((By.ID, "slr-checklist")))
        firefox.find_element_by_link_text("Checklist").click()

        checklist_text = wait_until(firefox.find_element_by_id, "slr-checklist").text
        assert "Make sure to do this and that." in checklist_text

    def test_shift_leader_no_checklist(self, live_server, firefox, shiftleader, wait):
        firefox.get('{}'.format(live_server.url))
        try_to_login_user(firefox, SHIFTLEADER_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Shift Leader")
        firefox.find_element_by_link_text("Shift Leader").click()
        wait.until(EC.presence_of_element_located((By.ID, "slr-checklist")))
        firefox.find_element_by_link_text("Checklist").click()

        checklist_text = wait_until(firefox.find_element_by_id, "slr-checklist").text
        assert "Make sure to do this and that." not in checklist_text
        assert "No shift leader checklist found." in checklist_text

    def test_shift_leader_popup(self, live_server, firefox, admin, wait):
        firefox.get('{}'.format(live_server.url))
        try_to_login_user(firefox, ADMIN_USERNAME, PASSWORD)
        wait_until(firefox.find_element_by_link_text, "Admin Settings").click()
        wait_until(firefox.find_element_by_link_text, "Global preferences").click()
        wait_until(firefox.find_element_by_link_text,
                   "shiftleader__popup_enabled").click()
        wait_until(firefox.find_element_by_id, "id_raw_value").click()
        firefox.find_element_by_name("_save").click()

        wait_until(firefox.find_element_by_link_text,
                   "shiftleader__popup_time_period").click()
        wait_until(firefox.find_element_by_id, "id_raw_value").clear()
        wait_until(firefox.find_element_by_id, "id_raw_value").send_keys("1")
        firefox.find_element_by_name("_save").click()

        wait_until(firefox.find_element_by_link_text, "VIEW SITE").click()
        wait_until(firefox.find_element_by_link_text, "Shift Leader").click()
        wait_until(firefox.find_element_by_tag_name, "h1")
        time.sleep(2)
        assert firefox.switch_to_alert().text == "Please perform the daily checks"
        firefox.switch_to_alert().accept()
        wait_until(firefox.find_element_by_link_text, "List of Certified Runs").click()

        wait_until(firefox.find_element_by_link_text, "Admin Settings").click()
        wait_until(firefox.find_element_by_link_text, "Global preferences").click()
        wait_until(firefox.find_element_by_link_text, "shiftleader__popup_text").click()
        wait_until(firefox.find_element_by_id, "id_raw_value").clear()
        wait_until(firefox.find_element_by_id, "id_raw_value") \
            .send_keys("Dont forget to do this and that.")
        firefox.find_element_by_name("_save").click()

        wait_until(firefox.find_element_by_link_text, "VIEW SITE").click()
        wait_until(firefox.find_element_by_link_text, "Shift Leader").click()
        wait_until(firefox.find_element_by_tag_name, "h1")
        time.sleep(2)
        assert firefox.switch_to_alert().text == "Dont forget to do this and that."
        firefox.switch_to_alert().accept()
        wait_until(firefox.find_element_by_link_text, "List of Certified Runs").click()

        wait_until(firefox.find_element_by_link_text, "Admin Settings").click()
        wait_until(firefox.find_element_by_link_text, "Global preferences").click()
        wait_until(firefox.find_element_by_link_text,
                   "shiftleader__popup_enabled").click()
        wait_until(firefox.find_element_by_id, "id_raw_value").click()
        firefox.find_element_by_name("_save").click()

        wait_until(firefox.find_element_by_link_text, "VIEW SITE").click()
        wait_until(firefox.find_element_by_link_text, "Shift Leader").click()
        wait_until(firefox.find_element_by_tag_name, "h1")
        time.sleep(3)
        with pytest.raises(NoAlertPresentException):
            firefox.switch_to_alert().accept()
        wait_until(firefox.find_element_by_link_text, "List of Certified Runs").click()
        wait_until(firefox.find_element_by_link_text, "Add Run").click()
