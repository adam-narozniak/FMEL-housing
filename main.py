import pyautogui
import argparse
import pathlib
import json
from mouse_input import *
from pynput import mouse
import time
import numpy as np
from numpy.random import default_rng
from datetime import datetime
import os
import datetime


def make_parser():
    parser = argparse.ArgumentParser(description="Tool to detect FMEL housing website changes")
    parser.add_argument("-out", "--output-directory", type=pathlib.Path, required=True,
                        help="Output directory where screenshots will be saved")
    parser.add_argument("-c", "--config-path", type=pathlib.Path, required=True,
                        help="Path to json file that specifies screen coordinates")
    parser.add_argument("-e", "--edit-screen-config", action="store_true", default=False,
                        help="If given then you will be asked to point left top and right bottom corners that specify "
                             "the rectangle that the image will be checked against")
    return parser


def check_screen_size_config_validity(clicks_coordinates):
    print(clicks_coordinates)
    assert clicks_coordinates[0]["x"] < clicks_coordinates[1]["x"]
    assert clicks_coordinates[0]["y"] < clicks_coordinates[1]["y"]
    print(f"Click configs are valid {clicks_coordinates}")


def read_screen_size_config(json_path):
    try:
        with open(json_path) as f:
            config = json.load(f)
            return config
    except Exception as e:
        print(e)


def get_screenshot_coordianates():
    # Collect events until released
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    return clicks_coordinates


if __name__ == '__main__':
    time.sleep(10)
    start_time = time.process_time()
    eight_o_clock = datetime.datetime.now().replace(hour=8, minute=0)
    parser = make_parser()
    args = parser.parse_args()
    output_directory = args.output_directory
    json_path = args.config_path
    if_edit_screen_config = args.edit_screen_config

    if if_edit_screen_config:
        # take user input to specify points
        print("Please click at the place that will be top left corner. "
              "Then click at the place that will be bottom right corner.")
        os.system("""spd-say "Please click at the place that will be top left corner. 
              Then click at the place that will be bottom right corner." -w""")
        clicks_coordinates = get_screenshot_coordianates()
        print(clicks_coordinates)
        with open("/home/adam/Documents/projects/python/FMEL_housing/resources/screen_size_config.json", "w") as f:
            json_dump= {
                "top_left":
                    {"x": clicks_coordinates[0]["x"], "y": clicks_coordinates[0]["y"]},
                "bottom_right":
                    {"x": clicks_coordinates[1]["x"], "y": clicks_coordinates[1]["y"]}
            }
            json.dump(json_dump, f, indent=4)
    else:
        # get the config from a file
        screen_config = read_screen_size_config(json_path)
        clicks_coordinates = [screen_config["top_left"], screen_config["bottom_right"]]
    check_screen_size_config_validity(clicks_coordinates)
    # this resource can be loaded in the beginning cause the refresh button won't change
    refresh_button_center_location = pyautogui.locateCenterOnScreen("./resources/refresh_button.png", grayscale=True,
                                                                    confidence=0.95)

    screenshot = pyautogui.screenshot()
    screenshot_name = "original_fmel_housing.jpg"
    screenshot_path = output_directory / screenshot_name
    print(screenshot_path)

    screenshot = screenshot.crop((clicks_coordinates[0]["x"], clicks_coordinates[0]["y"],
                                  clicks_coordinates[1]["x"], clicks_coordinates[1]["y"]))

    # screenshot.show()

    numpy_screenshot = np.array(screenshot)
    print(numpy_screenshot)
    rng = default_rng()
    while True:
        now = datetime.datetime.now()
        pyautogui.click(refresh_button_center_location)
        noise = rng.normal(loc=4, scale=2)
        sleep_time = max(0, 30 + noise)
        time.sleep(sleep_time)
        if now > eight_o_clock:
            new_screenshot = pyautogui.screenshot().crop((clicks_coordinates[0]["x"], clicks_coordinates[0]["y"],
                                                          clicks_coordinates[1]["x"], clicks_coordinates[1]["y"]))
            numpy_new_screenshot = np.array(new_screenshot)
            if not (numpy_screenshot == numpy_new_screenshot).all():
                # first try to log in again
                # TODO: implement logging in

                # 1a. If after refresh the page is the logging page then log in
                if False:  # (numpy_new_screenshot == numpy_logging_page).all():
                    log_in_button_center_location = pyautogui.locateCenterOnScreen("./resources/log_in_button.png")
                    pyautogui.click(log_in_button_center_location)
                # 1b. Else (there has been a new free place) => make a screenshot and start playing the sound
                else:
                    new_place_screenshot = pyautogui.screenshot(output_directory / "new_place.png")
                    select_button_center_location = pyautogui.locateCenterOnScreen("./resources/select_button.png",
                                                                                   confidence=0.90)
                    pyautogui.click(select_button_center_location)
                    print(
                        f"The page has changed at: {datetime.datetime.now()}.\nIt was after {10 * (time.process_time() - start_time)} seconds since the program got started")
                    while True:
                        os.system("""spd-say "Possibly there is a new free place at FMEL." -w""")
                        time.sleep(5)
            else:
                print("The site is the same")
