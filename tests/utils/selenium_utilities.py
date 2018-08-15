import time

from selenium.common.exceptions import WebDriverException, \
    ElementClickInterceptedException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def try_to_login_user(browser, username, password):
    browser.find_element_by_link_text("Login").click()
    browser.find_element_by_id("id_use_local_btn").click()
    browser.find_element_by_id("id_login").clear()
    browser.find_element_by_id("id_login").send_keys(username)
    browser.find_element_by_id("id_password").clear()
    browser.find_element_by_id("id_password").send_keys(password)
    browser.find_element_by_id("id_login_submit").click()


def add_some_reference_runs(browser):
    browser.find_element_by_link_text("Admin Settings").click()
    browser.find_element_by_css_selector(
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
    browser.find_element_by_link_text("ADD REFERENCE RUN").click()

    browser.find_element_by_id("id_reference_run").clear()
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

    browser.find_element_by_link_text("VIEW SITE").click()


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


def fill_and_submit_add_run_form(browser, wait):
    Select(browser.find_element_by_id("id_type")).select_by_index(1)
    browser.find_element_by_id("id_type").click()

    wait.until(EC.element_to_be_clickable((By.ID, "id_match_type")))
    browser.find_element_by_id("id_match_type").click()

    Select(browser.find_element_by_id("id_reference_run")).select_by_index(1)
    browser.find_element_by_id("id_reference_run").click()

    browser.find_element_by_id("id_run_number").click()
    browser.find_element_by_id("id_run_number").clear()
    browser.find_element_by_id("id_run_number").send_keys("456789")
    Select(browser.find_element_by_id("id_trackermap")).select_by_visible_text(
        "Exists")
    browser.find_element_by_id("id_trackermap").click()
    browser.find_element_by_id("id_number_of_ls").click()
    browser.find_element_by_id("id_number_of_ls").clear()
    browser.find_element_by_id("id_number_of_ls").send_keys("42")
    browser.find_element_by_id("id_int_luminosity").click()
    browser.find_element_by_id("id_int_luminosity").clear()
    browser.find_element_by_id("id_int_luminosity").send_keys("1.337")
    Select(browser.find_element_by_id("id_pixel")).select_by_visible_text("Good")
    browser.find_element_by_id("id_pixel").click()
    Select(browser.find_element_by_id("id_sistrip")).select_by_visible_text("Good")
    browser.find_element_by_id("id_sistrip").click()
    Select(browser.find_element_by_id("id_tracking")).select_by_visible_text("Good")
    browser.find_element_by_id("id_tracking").click()
    browser.find_element_by_id("id_submit_add_run").click()


def wait_for_dropdown_option(browser, option_text, MAX_WAIT=30):
    start_time = time.time()
    while True:
        try:
            table = browser.find_element_by_tag_name('table')
            cells = table.find_elements_by_tag_name('td')
            assert option_text in [cell.text for cell in cells]
            return
        except(AssertionError, WebDriverException) as e:
            if time.time() - start_time > MAX_WAIT:
                raise e
            time.sleep(0.1)


def wait_for_select_option(browser, text, MAX_WAIT=30):
    start_time = time.time()
    while True:
        try:
            options = browser.find_element_by_tag_name('option')
            assert text in [option.text for option in options]
            return
        except(AssertionError, WebDriverException) as e:
            if time.time() - start_time > MAX_WAIT:
                raise e
            time.sleep(0.1)


def wait_for_option_and_select(browser, select_id, MAX_WAIT=30):
    start_time = time.time()
    while True:
        try:
            select = browser.find_element_by_id(select_id)
            assert any(option.get_attribute("value") and
                       option.is_enabled()
                       for option
                       in select.find_elements_by_tag_name("option"))


        except(AssertionError, WebDriverException) as e:
            if time.time() - start_time > MAX_WAIT:
                raise e
            time.sleep(0.1)


def wait_for(browser, find_function, MAX_WAIT=30):
    start_time = time.time()
    while True:
        try:
            return find_function()
        except(AssertionError, WebDriverException) as e:
            if time.time() - start_time > MAX_WAIT:
                raise e
            time.sleep(0.1)


def wait_for_text_in_tag(browser, text, tag_name, MAX_WAIT=30):
    start_time = time.time()
    while True:
        try:
            cells = browser.find_elements_by_tag_name(tag_name)
            assert text in [cell.text for cell in cells]
            return
        except(AssertionError, WebDriverException) as e:
            if time.time() - start_time > MAX_WAIT:
                raise e
            time.sleep(0.1)


def wait_for_cell(browser, text, MAX_WAIT=30):
    wait_for_text_in_tag(browser, text, "td", MAX_WAIT)


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
