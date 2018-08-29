import time

from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

from tests.utils.wait import wait_until


def try_to_login_user(browser, username, password):
    browser.find_element_by_link_text("Login").click()
    wait_until(browser.find_element_by_id, "id_use_local_btn").click()
    browser.find_element_by_id("id_login").clear()
    browser.find_element_by_id("id_login").send_keys(username)
    browser.find_element_by_id("id_password").clear()
    browser.find_element_by_id("id_password").send_keys(password)
    browser.find_element_by_id("id_login_submit").click()


def add_some_reference_runs(browser):
    browser.find_element_by_link_text("Admin Settings").click()
    wait_until(browser.find_element_by_css_selector,
               "tr.model-referencerun > td > a.addlink").click()
    browser.find_element_by_id("id_reference_run").clear()
    browser.find_element_by_id("id_reference_run").send_keys("1")
    Select(browser.find_element_by_id("id_reco")).select_by_visible_text("Express")
    Select(browser.find_element_by_id("id_runtype")).select_by_visible_text("Cosmics")
    Select(browser.find_element_by_id("id_bfield")).select_by_visible_text("0 T")
    Select(browser.find_element_by_id("id_beamtype")).select_by_visible_text("Cosmics")
    Select(browser.find_element_by_id("id_beamenergy")).select_by_visible_text(
        "Cosmics")
    browser.find_element_by_id("id_dataset").clear()
    browser.find_element_by_id("id_dataset").send_keys("/some/dataset")
    browser.find_element_by_name("_save").click()
    wait_until(browser.find_element_by_link_text, "ADD REFERENCE RUN").click()

    wait_until(browser.find_element_by_id, "id_reference_run").clear()
    browser.find_element_by_id("id_reference_run").send_keys("2")
    Select(browser.find_element_by_id("id_reco")).select_by_visible_text("Prompt")
    Select(browser.find_element_by_id("id_runtype")).select_by_visible_text(
        "Collisions")
    browser.find_element_by_id("id_runtype").click()
    Select(browser.find_element_by_id("id_bfield")).select_by_visible_text("3.8 T")
    browser.find_element_by_id("id_bfield").click()
    Select(browser.find_element_by_id("id_beamtype")).select_by_visible_text(
        "Proton-Proton")
    browser.find_element_by_id("id_beamtype").click()
    Select(browser.find_element_by_id("id_beamenergy")).select_by_visible_text("13 TeV")
    browser.find_element_by_id("id_beamenergy").click()
    browser.find_element_by_id("id_dataset").click()
    browser.find_element_by_id("id_dataset").clear()
    browser.find_element_by_id("id_dataset").send_keys("/bla/blubb")
    browser.find_element_by_name("_save").click()

    wait_until(browser.find_element_by_link_text, "VIEW SITE").click()


def check_checklist(browser, wait, name):
    browser.find_element_by_id("id_checklist_{}".format(name)).click()
    browser.find_element_by_id("id_btn_checkall_{}".format(name)).click()
    browser.find_element_by_id("id_submit_checklist_{}".format(name)).click()
    wait.until(EC.invisibility_of_element_located((By.ID, "modal-{}-id".format(name))))
    wait.until(EC.invisibility_of_element_located(
        (By.CLASS_NAME, "modal-backdrop ".format(name))))


def check_all_checklists(browser, wait):
    check_checklist(browser, wait, "general")
    check_checklist(browser, wait, "trackermap")
    check_checklist(browser, wait, "pixel")
    check_checklist(browser, wait, "sistrip")
    check_checklist(browser, wait, "tracking")


def fill_form_with_data(browser, data=None):
    if data is None:
        data = {}
    browser.find_element_by_id("id_run_number").click()
    browser.find_element_by_id("id_run_number").clear()
    browser.find_element_by_id("id_run_number").send_keys(
        data.get("run_number", "456789"))
    Select(browser.find_element_by_id("id_trackermap")).select_by_visible_text(
        data.get("trackermap", "Exists"))
    browser.find_element_by_id("id_number_of_ls").clear()
    browser.find_element_by_id("id_number_of_ls").send_keys(
        data.get("number_of_ls", "42"))  #
    browser.find_element_by_id("id_int_luminosity").clear()
    browser.find_element_by_id("id_int_luminosity").send_keys(
        data.get("int_luminosity", "1.337"))
    Select(browser.find_element_by_id("id_pixel")).select_by_visible_text(
        data.get("pixel", "Good"))
    Select(browser.find_element_by_id("id_sistrip")).select_by_visible_text(
        data.get("sistrip", "Good"))
    Select(browser.find_element_by_id("id_tracking")).select_by_visible_text(
        data.get("tracking", "Good"))


def select_types_and_reference_runs_in_form(browser):
    wait_until(Select(browser.find_element_by_id("id_type")).select_by_index, 1)
    time.sleep(0.1)
    options = browser.find_elements_by_css_selector(
        "select#id_reference_run > option:not([disabled])")
    the_value = None
    for option in options:
        the_value = option.get_attribute("value")
        if the_value != "":
            break

    wait_until(Select(browser.find_element_by_id("id_reference_run")).select_by_value,
               the_value)


def fill_and_submit_add_run_form(browser):
    select_types_and_reference_runs_in_form(browser)
    fill_form_with_data(browser)
    browser.find_element_by_id("id_submit_add_run").click()


def click_checklist_checkbox(browser, checklist_id, MAX_WAIT=30):
    start_time = time.time()
    while True:
        try:
            browser.find_element_by_id(checklist_id).click()
        except ElementClickInterceptedException as e:
            if time.time() - start_time > MAX_WAIT:
                raise e
            time.sleep(0.1)


def set_shift_leader_filter_date(browser, year_0, month_0, day_0, year_1, month_1,
                                 day_1):
    """
    Selects the filter date in the Shift Leader Page to the given parameters
    and submits the form
    """
    Select(browser.find_element_by_id("id_date__gte_month")).select_by_visible_text(
        month_0)
    Select(browser.find_element_by_id("id_date__gte_day")).select_by_visible_text(
        day_0)
    Select(browser.find_element_by_id("id_date__gte_year")).select_by_visible_text(
        year_0)
    Select(browser.find_element_by_id("id_date__lte_month")).select_by_visible_text(
        month_1)
    Select(browser.find_element_by_id("id_date__lte_day")).select_by_visible_text(
        day_1)
    Select(browser.find_element_by_id("id_date__gte_year")).select_by_visible_text(
        year_1)
    browser.find_element_by_id("id_btn_filter").click()
