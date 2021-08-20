import argparse
import datetime
import json
import os
import pathlib
import platform
import time

import selenium
import selenium.common.exceptions
import yagmail
from selenium import webdriver

FMEL_CREDENTIALS_CONFIGURATION_PATH = "./resources/credentials_config.json"
EMAIL_CREDENTIALS_CONFIGURATION_PATH = "./resources/email_credentials_config.json"
START_PAGE = "https://accommodation.fmel.ch/StarRezPortal/83D6F19F/71/923/Book_now-Contract_dates"


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
    if date == "16/08":
        driver.find_element_by_xpath("/html/body/div[2]/section[1]/div/article/div/div/div/"
                                     "section/div[1]/section/form/div/div[2]/div[2]/button").click()
    elif date == "01/09":
        driver.find_element_by_xpath("/html/body/div[2]/section[1]/div/article/div/div/div/"
                                     "section/div[1]/section/form/div/div[3]/div[2]/button").click()
    elif date == "16/09":
        target = driver.find_element_by_xpath("/html/body/div[2]/section[1]/div/article/div/div/div/"
                                              "section/div[1]/section/form/div/div[4]/div[2]/button")
        driver.execute_script('arguments[0].scrollIntoView(true);', target)
        target.click()
    elif date == "01/10":
        target = driver.find_element_by_xpath("/html/body/div[2]/section[1]/div/article/div/div/div/"
                                              "section/div[1]/section/form/div/div[5]/div[2]/button")
        driver.execute_script('arguments[0].scrollIntoView(true);', target)
        target.click()
    elif date == "16/10":
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


def sound_notification(duration, date):
    system_name = platform.system()
    if system_name == "Darwin" or system_name == "Linux":
        delta = datetime.timedelta(seconds=duration)
        begin_time = datetime.datetime.now()
        now = datetime.datetime.now()
        while now < begin_time + delta:
            os.system(f"""say "Possibly there is a new free place at FMEL on the {date}" """)
            now = datetime.datetime.now()
    else:
        raise Exception(f"System not supported")


def set_up_email(email_username, email_password):
    """Sets up email connection and returns email manager object."""
    yag = yagmail.SMTP(email_username, email_password)
    return yag


def prepare_dirs():
    page_sources = pathlib.Path("./page_sources")
    page_sources.mkdir(exist_ok=True)
    ps_after_book_was_clicked = page_sources / "after_book_was_clicked"
    ps_after_book_was_clicked.mkdir(exist_ok=True)
    ps_after_select_was_clicked = page_sources / "after_select_was_clicked"
    ps_after_select_was_clicked.mkdir(exist_ok=True)
    screenshots = pathlib.Path("./screenshots")
    screenshots.mkdir(exist_ok=True)
    sc_after_book_was_clicked = screenshots / "after_book_was_clicked"
    sc_after_book_was_clicked.mkdir(exist_ok=True)
    sc_after_select_was_clicked = screenshots / "after_select_was_clicked"
    sc_after_select_was_clicked.mkdir(exist_ok=True)


def main():
    parser = make_parser()
    args = parser.parse_args()
    mode = args.mode
    date = args.date
    prepare_dirs()
    fmel_username, fmel_password = get_credentials(FMEL_CREDENTIALS_CONFIGURATION_PATH)
    if mode == "email":
        email_username, email_password = get_credentials(EMAIL_CREDENTIALS_CONFIGURATION_PATH)
        yag = set_up_email(email_username, email_password)
        to = email_username
        subject = "Possibly a new free place at FMEL"
    driver = webdriver.Chrome()
    driver.maximize_window()
    was_outside_working_hours = True
    while True:
        now = datetime.datetime.now().hour
        if 8 <= now < 18:
            # log in for the first time/ you were in inactive hours so probably log in is needed
            if was_outside_working_hours:
                go_to_booking(driver, fmel_username, fmel_password, date)
                was_outside_working_hours = False
            try:
                driver.refresh()
            except selenium.common.exceptions.TimeoutException:
                time.sleep(5)
                continue
            refreshed_page = driver.page_source
            if refreshed_page.find("This page isn’t working") != -1 or refreshed_page == "":
                continue
            # there is no string indicating no places available
            if refreshed_page.find("Please check regularly for new availabilities") == -1:
                change_time = datetime.datetime.now()
                print(f"page has changed at {change_time}!")
                with open(f"./page_sources/ps_for_{date.replace('/', '.')}_{change_time}.txt", "w") as f:
                    f.write(driver.page_source)
                # target = driver.find_element_by_xpath("/html/body/div[2]/section[1]/div/article/div/div/div/section/"
                #                                       "div[1]/section/form/div/div[2]/div[2]/div/div[2]/button")
                # driver.execute_script('arguments[0].scrollIntoView(true);', target)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                driver.save_screenshot(f"./screenshots/fmel_{date.replace('/', '.')}_{change_time}.png")
                # # click select button
                # target.click()
                # driver.implicitly_wait(0.3)
                # with open(f"./page_sources/after_select_was_clicked/ps_for_{date.replace('/', '.')}_{change_time}.txt",
                #           "w") as f:
                #     f.write(driver.page_source)
                # driver.save_screenshot(
                #     f"./screenshots/after_select_was_clicked/fmel_{date.replace('/', '.')}_{change_time}.png")
                # # click book now
                # book_button = driver.find_element_by_xpath("/html/body/div[2]/section[1]/div/article/div/div/div/"
                #                                            "section/div[1]/section/form/div/div[2]/div[2]/div[1]/"
                #                                            "div[1]/div[3]/button[1]")
                # book_button.click()
                # driver.implicitly_wait(0.3)
                # with open(f"./page_sources/after_book_was_clicked/ps_for_{date.replace('/', '.')}_{change_time}.txt",
                #           "w") as f:
                #     f.write(driver.page_source)
                # driver.save_screenshot(
                #     f"./screenshots/after_book_was_clicked/fmel_{date.replace('/', '.')}_{change_time}.png")
                # notify about that
                if mode == "voice":
                    sound_notification(300, date)
                    break
                elif mode == "email":
                    # send an email and go back to checking availability after 5 minutes
                    yag.send(to, subject, f"Check this page for date {date}:\n{driver.current_url}")
                    time.sleep(300)
        else:
            was_outside_working_hours = True
            time.sleep(300)


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(e)
            os.system("""say "Exception occurred" """)
