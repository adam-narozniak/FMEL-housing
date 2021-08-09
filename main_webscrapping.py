import json
import os
import platform
from datetime import datetime

from selenium import webdriver

CREDENTIALS_CONFIGURATION_PATH = "./resources/credentials_config.json"
START_PAGE = "https://accommodation.fmel.ch/StarRezPortal/83D6F19F/71/923/Book_now-Contract_dates"
# START_PAGE = "https://accommodation.fmel.ch/StarRezPortal/AA222FD0/71/929/Book_now-House_selection?TermID=1302&ClassificationID=1&DateStart=16%20August%202021&DateEnd=15%20August%202026"


def log_in(driver, username, password):
    username_field = driver.find_element_by_name("Username")
    username_field.clear()
    username_field.send_keys(username)

    password_field = driver.find_element_by_name("Password")
    password_field.clear()
    password_field.send_keys(password)

    driver.find_element_by_class_name("login-button").click()
    print("log in done")


def go_to_booking(driver, username, password):
    driver.get(START_PAGE)
    log_in(driver, username, password)
    driver.implicitly_wait(4)
    # 16/08
    driver.find_element_by_xpath(
        "/html/body/div[2]/section[1]/div/article/div/div/div/section/div[1]/section/form/div/div[3]/div[2]/button").click()
    # 01/09
    # /html/body/div[2]/section[1]/div/article/div/div/div/section/div[1]/section/form/div/div[4]/div[2]/button
    # 16/09
    # /html/body/div[2]/section[1]/div/article/div/div/div/section/div[1]/section/form/div/div[5]/div[2]/button


def get_credentials():
    with open(CREDENTIALS_CONFIGURATION_PATH, "r") as f:
        credentials_dict = json.load(f)
    username, password = credentials_dict["login"], credentials_dict["password"]
    if username == "" or password == "":
        raise Exception(f"Please specify username and password in {CREDENTIALS_CONFIGURATION_PATH} file.")
    return username, password


def sound_notification():
    system_name = platform.system()
    if system_name == "Darwin":
        os.system("""say "Possibly there is a new free place at FMEL." """)
    elif system_name == "Linux":
        os.system("""spd-say "Possibly there is a new free place at FMEL." -w""")
    else:
        raise Exception(f"System not supported")


if __name__ == "__main__":
    username, password = get_credentials()
    driver = webdriver.Chrome()
    was_outside_working_hours = True
    while True:
        now = datetime.now().hour
        if 6 <= now < 18:
            # log in for the first time/ you were in inactive hours so probably log in is needed
            if was_outside_working_hours:
                go_to_booking(driver, username, password)
                was_outside_working_hours = False
            driver.implicitly_wait(4)
            driver.refresh()
            refreshed_page = driver.page_source
            # there is no string indicating no places available
            if refreshed_page.find("Please check regularly for new availabilities") == -1:
                print("page has changed!")
                # notify about that
                while True:
                    sound_notification()
        else:
            was_outside_working_hours = True
