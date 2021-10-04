import argparse
import datetime
import json
import logging
import os
import pathlib
import platform
import time
import sys

import selenium
import selenium.common.exceptions
import pyttsx3
import yagmail
from selenium import webdriver

import logger_module

FMEL_CREDENTIALS_CONFIGURATION_PATH = "./resources/credentials_config.json"
EMAIL_CREDENTIALS_CONFIGURATION_PATH = "./resources/email_credentials_config.json"
START_PAGE = "https://accommodation.fmel.ch/StarRezPortal/83D6F19F/71/923/Book_now-Contract_dates"
logger_module.setup_logger()
logger = logging.getLogger("FMEL_HOUSING.main")


def make_parser():
    parser = argparse.ArgumentParser(description="Tool to detect FMEL housing website changes")
    parser.add_argument("-m", "--mode", type=str, required=False, default="voice",
                        help="Choose between voice, email and both notifications. [voice|email|mix]")
    parser.add_argument("-d", "--date", type=str, required=False, default="16/09",
                        help="Rent starting date in format date/month.")
    parser.add_argument("-f", "--full_automation", required=False, action="store_true",
                        help="This flag allows to put the appearing offer to a basket. "
                             "That way your reservation will be saved for the next 30 minutes.")
    parser.add_argument("-r", "--refresh_rate", required=False, default=2.5, type=int,
                        help="Refresh rate in seconds. Every x seconds page will be refreshed.")
    return parser


def log_in(driver, username, password):
    logger.debug("Logging in")
    username_field = driver.find_element_by_name("Username")
    username_field.clear()
    username_field.send_keys(username)

    password_field = driver.find_element_by_name("Password")
    password_field.clear()
    password_field.send_keys(password)

    driver.find_element_by_class_name("login-button").click()


def go_to_booking(driver, username, password, date):
    driver.get(START_PAGE)
    log_in(driver, username, password)
    logger.info("Log in done")
    logger.debug("Try to go the page starting with the given date")
    if date == "16/10":
        target = driver.find_element_by_xpath("/html/body/div[2]/section[1]/div/article/div/div/div/"
                                              "section/div[1]/section/form/div/div[3]/div[2]/button")
        driver.execute_script('arguments[0].scrollIntoView(true);', target)
        target.click()
    elif date == "01/11":
        target = driver.find_element_by_xpath("/html/body/div[2]/section[1]/div/article/div/div/div/"
                                              "section/div[1]/section/form/div/div[4]/div[2]/button")
        driver.execute_script('arguments[0].scrollIntoView(true);', target)
        target.click()
    elif date == "16/11":
        target = driver.find_element_by_xpath("/html/body/div[2]/section[1]/div/article/div/div/div/"
                                              "section/div[1]/section/form/div/div[5]/div[2]/button")
        driver.execute_script('arguments[0].scrollIntoView(true);', target)
        target.click()
    elif date == "01/12":
        target = driver.find_element_by_xpath("/html/body/div[2]/section[1]/div/article/div/div/div/"
                                              "section/div[1]/section/form/div/div[6]/div[2]/button")
        driver.execute_script('arguments[0].scrollIntoView(true);', target)
        target.click()
    else:
        raise Exception(f"Given date: {date} is not supported")

    logger.info("Date chosen")


def get_credentials(credentials_configuration_path):
    with open(credentials_configuration_path, "r") as f:
        credentials_dict = json.load(f)
    username, password = credentials_dict["login"], credentials_dict["password"]
    if username == "" or password == "":
        raise Exception(f"Please specify username and password in {credentials_configuration_path} file.")
    return username, password


def sound_notification(duration, date):
    logger.debug("Try to sound-notify")
    system_name = platform.system()
    now = datetime.datetime.now()
    delta = datetime.timedelta(seconds=duration)
    begin_time = datetime.datetime.now()
    if system_name == "Darwin" or system_name == "Linux":
        while now < begin_time + delta:
            os.system(f"""say "Possibly there is a new free place at FMEL on the {date}" """)
            now = datetime.datetime.now()
    elif system_name.lower() == "windows":
        engine = pyttsx3.init()
        while now < begin_time + delta:
            engine.say(f"Possibly there is a new free place at FMEL on the {date}")
            engine.runAndWait()
    else:
        raise Exception(f"System not supported")


def set_up_email(email_username, email_password):
    """Sets up email connection and returns email manager object."""
    logger.debug("Setting up email manager")
    yag = yagmail.SMTP(email_username, email_password)
    return yag


def prepare_dirs():
    logger.debug("Creating directories")
    page_sources = pathlib.Path("./page_sources")
    page_sources.mkdir(exist_ok=True)
    new_offers = page_sources / "new_offers"
    new_offers.mkdir(exist_ok=True)
    ps_after_book_was_clicked = page_sources / "after_book_was_clicked"
    ps_after_book_was_clicked.mkdir(exist_ok=True)
    ps_after_select_was_clicked = page_sources / "after_select_was_clicked"
    ps_after_select_was_clicked.mkdir(exist_ok=True)
    screenshots = pathlib.Path("./screenshots")
    screenshots.mkdir(exist_ok=True)
    sc_new_offers = screenshots / "new_offers"
    sc_new_offers.mkdir(exist_ok=True)
    sc_after_book_was_clicked = screenshots / "after_book_was_clicked"
    sc_after_book_was_clicked.mkdir(exist_ok=True)
    sc_after_select_was_clicked = screenshots / "after_select_was_clicked"
    sc_after_select_was_clicked.mkdir(exist_ok=True)


def main(driver):
    parser = make_parser()
    args = parser.parse_args()
    mode = args.mode
    date = args.date
    full_automation = args.full_automation
    refresh_rate = args.refresh_rate
    prepare_dirs()
    logger.info("Directories created")
    fmel_username, fmel_password = get_credentials(FMEL_CREDENTIALS_CONFIGURATION_PATH)
    logger.info("Credentials loaded")
    if mode == "email" or mode == "mix":
        email_username, email_password = get_credentials(EMAIL_CREDENTIALS_CONFIGURATION_PATH)
        yag = set_up_email(email_username, email_password)
        to = email_username
        subject = "Possibly a new free place at FMEL"
    driver.implicitly_wait(5)
    driver.maximize_window()
    was_outside_working_hours = True
    while True:
        now = datetime.datetime.now().hour
        if 8 <= now < 20:
            # log in for the first time/ you were in inactive hours so probably log in is needed
            if was_outside_working_hours:
                go_to_booking(driver, fmel_username, fmel_password, date)
                was_outside_working_hours = False
            try:
                time.sleep(refresh_rate)
                driver.refresh()
            except selenium.common.exceptions.TimeoutException:
                time.sleep(5)
                continue
            refreshed_page = driver.page_source
            if refreshed_page.find("This page isn’t working") != -1 or refreshed_page == "" or \
                    refreshed_page.find("You don't have permission to access this resource.") != -1 or \
                    refreshed_page.find("This site can’t be reached") != -1:
                continue
            # there is no string indicating no places available
            if refreshed_page.find("Please check regularly for new availabilities") == -1:
                logger.info("New place is available")
                change_time = datetime.datetime.now()
                print(f"page has changed at {change_time}!")
                with open(f"./page_sources/new_offers/fmel_offer_starting_{date.replace('/', '.')}"
                          f"_found_{str(change_time).replace(':', '-')}.txt", "w") as f:
                    f.write(driver.page_source)
                # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                target = driver.find_element_by_xpath(
                    "/html/body/div[2]/section[1]/div/article/div/div/div/section/div[1]/section/form/div/"
                    "div[2]/div[2]/div/div[2]/button")
                driver.execute_script('arguments[0].scrollIntoView(true);', target)
                driver.save_screenshot(f"./screenshots/new_offers/fmel_offer_starting_{date.replace('/', '.')}_"
                                       f"found_{str(change_time).replace(':', '-')}.png")
                time.sleep(0.3)
                if full_automation is True:
                    # click select button
                    target.click()
                    with open(f"./page_sources/after_select_was_clicked/fmel_offer_starting_{date.replace('/', '.')}"
                              f"_found_{str(change_time).replace(':', '-')}.txt", "w") as f:
                        f.write(driver.page_source)
                    driver.save_screenshot(
                        f"./screenshots/after_select_was_clicked/fmel_offer_starting_{date.replace('/', '.')}"
                        f"_found_{str(change_time).replace(':', '-')}.png")
                    # click 'book now'
                    book_button = driver.find_element_by_xpath("/html/body/div[2]/section[1]/div/article/div/div/div/"
                                                               "section/div[1]/section/form/div/div[2]/div[2]/div[1]/"
                                                               "div[1]/div[3]/button[1]")
                    book_button.click()
                    time.sleep(0.3)

                    with open(f"./page_sources/after_book_was_clicked/fmel_offer_starting_{date.replace('/', '.')}"
                              f"_found_{str(change_time).replace(':', '-')}.txt", "w") as f:
                        f.write(driver.page_source)
                    driver.save_screenshot(
                        f"./screenshots/after_book_was_clicked/fmel_offer_starting_{date.replace('/', '.')}"
                        f"_found_{str(change_time).replace(':', '-')}.png")
                logger.debug("Try to notify")
                # notify about that
                if mode == "voice":
                    sound_notification(300, date)
                elif mode == "email":
                    # send an email and go back to checking availability after 5 minutes
                    yag.send(to, subject + " starting " + date,
                             f"Check this page for date {date}:\n{driver.current_url}")
                elif mode == "mix":
                    yag.send(to, subject + " starting " + date,
                             f"Check this page for date {date}:\n{driver.current_url}")
                    sound_notification(300, date)
                logger.info("Notification sent")
                sys.exit(1)
        else:
            was_outside_working_hours = True
            time.sleep(300)


if __name__ == "__main__":
    while True:
        try:
            driver = webdriver.Chrome()
            main(driver)
        except Exception as e:
            driver.quit()
            logger.exception(e)
            print("Let the programmer know that the exception occurred to make this program work better.")
