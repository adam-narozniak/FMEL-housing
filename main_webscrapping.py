import argparse
import json
import os
import platform
import time
from datetime import datetime
import yagmail

import selenium.common.exceptions
from selenium import webdriver

FMEL_CREDENTIALS_CONFIGURATION_PATH = "./resources/credentials_config.json"
EMAIL_CREDENTIALS_CONFIGURATION_PATH = "./resources/email_credentials_config.json"
START_PAGE = "https://accommodation.fmel.ch/StarRezPortal/83D6F19F/71/923/Book_now-Contract_dates"
# START_PAGE = "https://accommodation.fmel.ch/StarRezPortal/AA222FD0/71/929/Book_now-House_selection?TermID=1302&ClassificationID=1&DateStart=16%20August%202021&DateEnd=15%20August%202026"

def make_parser():
    parser = argparse.ArgumentParser(description="Tool to detect FMEL housing website changes")
    parser.add_argument("-m", "--mode", type=str, required=False, default="voice",
                        help="Choose between voice and email notification. [voice|email]")
    parser.add_argument("-d", "--date", type=str, required=False, default="16/08",
                        help="Rent starting date: 16/08 or 01/09 or 16/09")
    return parser


def log_in(driver, username, password):
    username_field = driver.find_element_by_name("Username")
    username_field.clear()
    username_field.send_keys(username)

    password_field = driver.find_element_by_name("Password")
    password_field.clear()
    password_field.send_keys(password)

    driver.find_element_by_class_name("login-button").click()
    print("log in done")


def go_to_booking(driver, username, password, date):
    driver.get(START_PAGE)
    log_in(driver, username, password)
    driver.implicitly_wait(4)
    if date == "01/08":
        driver.find_element_by_xpath("/html/body/div[2]/section[1]/div/article/div/div/div/"
                                     "section/div[1]/section/form/div/div[2]/div[2]/button").click()
    elif date == "16/08":
        driver.find_element_by_xpath("/html/body/div[2]/section[1]/div/article/div/div/div/"
                                     "section/div[1]/section/form/div/div[3]/div[2]/button").click()
    elif date == "01/09":
        driver.find_element_by_xpath("/html/body/div[2]/section[1]/div/article/div/div/div/"
                                     "section/div[1]/section/form/div/div[4]/div[2]/button").click()
    elif date == "16/09":
        target = driver.find_element_by_xpath("/html/body/div[2]/section[1]/div/article/div/div/div/"
                                              "section/div[1]/section/form/div/div[5]/div[2]/button")
        driver.execute_script('arguments[0].scrollIntoView(true);', target)
        target.click()
    elif date == "01/10":
        target = driver.find_element_by_xpath("/html/body/div[2]/section[1]/div/article/div/div/div/"
                                              "section/div[1]/section/form/div/div[6]/div[2]/button")
        driver.execute_script('arguments[0].scrollIntoView(true);', target)
        target.click()
    else:
        raise Exception(f"Given date: {date} is not supported")


def get_credentials(credentials_configuration_path):
    with open(credentials_configuration_path, "r") as f:
        credentials_dict = json.load(f)
    username, password = credentials_dict["login"], credentials_dict["password"]
    if username == "" or password == "":
        raise Exception(f"Please specify username and password in {credentials_configuration_path} file.")
    return username, password


def sound_notification():
    system_name = platform.system()
    if system_name == "Darwin" or system_name == "Linux":
        os.system("""say "Possibly there is a new free place at FMEL." """)
    else:
        raise Exception(f"System not supported")


def set_up_email(email_username, email_password):
    """Sets up email connection and returns email manager object."""
    yag = yagmail.SMTP(email_username, email_password)
    return yag


if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args()
    mode = args.mode
    date = args.date
    fmel_username, fmel_password = get_credentials(FMEL_CREDENTIALS_CONFIGURATION_PATH)
    if mode == "email":
        email_username, email_password = get_credentials(EMAIL_CREDENTIALS_CONFIGURATION_PATH)
        yag = set_up_email(email_username, email_password)
        to = email_username
        subject = "Possibly a new free place at FMEL"
    driver = webdriver.Chrome()
    was_outside_working_hours = True
    while True:
        now = datetime.now().hour
        if True:  # 6 <= now < 18:
            # log in for the first time/ you were in inactive hours so probably log in is needed
            if was_outside_working_hours:
                go_to_booking(driver, fmel_username, fmel_password, date)
                was_outside_working_hours = False
            try:
                driver.refresh()
            except selenium.common.exceptions.TimeoutException:
                driver.refresh()
            refreshed_page = driver.page_source
            # there is no string indicating no places available
            if refreshed_page.find("Please check regularly for new availabilities") == -1:
                print("page has changed!")
                print(driver.page_source)
                # notify about that
                if mode == "voice":
                    while True:
                        sound_notification()
                elif mode == "email":
                    # send an email and go back to checking availability after 5 minutes
                    yag.send(to, subject, f"Check this page:\n{driver.current_url}")
                    time.sleep(300)
        else:
            was_outside_working_hours = True
            time.sleep(60)
