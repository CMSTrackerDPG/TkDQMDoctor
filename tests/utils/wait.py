import time

from selenium.common.exceptions import WebDriverException, NoSuchElementException


def wait_until(find_function, find_function_argument, MAX_WAIT=30):
    start_time = time.time()
    while True:
        try:
            return find_function(find_function_argument)
        except NoSuchElementException as e:
            if time.time() - start_time > MAX_WAIT:
                raise e
            time.sleep(0.1)


def wait_for_dropdown_option(browser, option_text, MAX_WAIT=30):
    start_time = time.time()
    while True:
        try:
            table = browser.find_element_by_tag_name("table")
            cells = table.find_elements_by_tag_name("td")
            assert option_text in [cell.text for cell in cells]
            return
        except (AssertionError, WebDriverException) as e:
            if time.time() - start_time > MAX_WAIT:
                raise e
            time.sleep(0.1)


def wait_for_select_option(browser, text, MAX_WAIT=30):
    start_time = time.time()
    while True:
        try:
            options = browser.find_element_by_tag_name("option")
            assert text in [option.text for option in options]
            return
        except (AssertionError, WebDriverException) as e:
            if time.time() - start_time > MAX_WAIT:
                raise e
            time.sleep(0.1)


def wait_for_option_and_select(browser, select_id, MAX_WAIT=30):
    start_time = time.time()
    while True:
        try:
            select = browser.find_element_by_id(select_id)
            assert any(
                option.get_attribute("value") and option.is_enabled()
                for option in select.find_elements_by_tag_name("option")
            )
        except (AssertionError, WebDriverException) as e:
            if time.time() - start_time > MAX_WAIT:
                raise e
            time.sleep(0.1)


def wait_for(browser, find_function, MAX_WAIT=30):
    start_time = time.time()
    while True:
        try:
            return find_function()
        except (AssertionError, WebDriverException) as e:
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
        except (AssertionError, WebDriverException):
            if time.time() - start_time > MAX_WAIT:
                raise TimeoutError
            time.sleep(0.1)


def wait_for_cell(browser, text, MAX_WAIT=30):
    wait_for_text_in_tag(browser, text, "td", MAX_WAIT)
