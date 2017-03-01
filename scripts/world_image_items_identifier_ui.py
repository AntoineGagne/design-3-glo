import cv2

from enum import IntEnum, unique
from typing import Tuple
import os
import json
import sys


@unique
class KeycodeValues(IntEnum):
    """Some of the key codes of OpenCV."""
    key_space = 32
    digit_zero = 48
    digit_one = 49
    digit_two = 50
    digit_three = 51
    digit_four = 52
    digit_eight = 56
    digit_nine = 57
    key_r = 114
    key_e = 101


class WorldItemsManualDetector:
    def __init__(self, directory_path):
        self._initialize_keypress_handler()
        self.images_directory_path = directory_path
        self.coordinates = {"upper-left": (0, 0)}
        self.key = "upper-left"

        self.image_path = None

        cv2.namedWindow("image")
        cv2.setMouseCallback("image", self.set_coordinates)

    def _initialize_keypress_handler(self):
        """Initialize the keypress handler."""
        self.keypress_handler = {KeycodeValues.key_e: self._remove_coordinates}
        self._initialize_drawing_zone_handlers()
        self._initialize_game_element_handlers()

    def _initialize_drawing_zone_handlers(self):
        """Initialize the drawing zone keypress handlers."""
        items = [(KeycodeValues.digit_one, 'upper-left'),
                 (KeycodeValues.digit_two, 'upper-right'),
                 (KeycodeValues.digit_three, 'lower-left'),
                 (KeycodeValues.digit_four, 'lower-right')]

        for key, value in items:
            self.keypress_handler[key] = self._handle_keypress(
                *_format_drawing_zone_message(value)
            )

    def _initialize_game_element_handlers(self):
        """Initialize the game element keypress handlers."""
        items = [(KeycodeValues.digit_zero, 'obstacle1', 'first obstacle'),
                 (KeycodeValues.digit_eight, 'obstacle3', 'third obstacle'),
                 (KeycodeValues.digit_nine, 'obstacle2', 'second obstacle'),
                 (KeycodeValues.key_r, 'robot', 'robot')]

        for key, value, message in items:
            self.keypress_handler[key] = self._handle_keypress(
                value,
                _format_element_message(message)
            )

    def iterate_images(self):
        for filename in os.listdir(self.images_directory_path):
            if filename.endswith((".jpg", ".png")):
                image_path = os.path.join(self.images_directory_path, filename)
                self.image_path = image_path
                self.reset_data()
                self.enter_loop()
                self.record_data()
        print("This is the end! Thank you!")

    # define mouse callback function
    def set_coordinates(self, event, x, y, *args):
        if event == cv2.EVENT_LBUTTONDOWN:
            print('The coordinates you have set for {0} are ({1}, '
                  '{2})'.format(self.key, x, y))
            self.coordinates[self.key] = (x, y)

    def reset_data(self):
        self.coordinates = {"upper-left": (0, 0)}

    def enter_loop(self):
        key = -1
        while key != KeycodeValues.key_space:
            loaded_image = cv2.imread(self.image_path)
            cv2.imshow('image', loaded_image)
            # 0xFF for masking last 8 bits of value
            key = cv2.waitKey(33)
            if key in self.keypress_handler:
                print(self.keypress_handler[key]())
            else:
                continue

    def _handle_keypress(self, value: str, message: str):
        """A keypress handler.

        :param value: The value with which to update the *key* attribute
        :param message: The message to display when updating the attribute
        :returns: A function that will be called when the handling is done
        """
        def wrapped_handler() -> str:
            """Update the *key* attribute and return a message.

            :returns: A message concerning the update
            :rtype: str
            """
            self.key = value
            return message

        return wrapped_handler

    def _remove_coordinates(self) -> str:
        """Remove the coordinates for the given *key* attribute.

        :returns: A message with the status of the removal
        :rtype: str
        """
        message = ('Nothing erased, there were no coordinates '
                   'found for {0}').format(self.key)
        if self.key in self.coordinates:
            self.coordinates.pop(self.key)
            message = 'Erased {} coordinates'.format(self.key)

        return message

    def record_data(self):
        data_file_name = '{}.json'.format(self.image_path)
        with open(data_file_name, 'w', encoding='utf-8') as output_file:
            json.dump(self.coordinates, output_file)


def _format_drawing_zone_message(value: str) -> Tuple[str, str]:
    """Create a drawing zone message from the given value.

    :param value: The value to update (i.e. upper-left, upper-right, ...)
    :type value: str
    :returns: A tuple containing the value and the message
    """
    return value, 'Click on the {0} corner of the drawing zone.'.format(value)


def _format_element_message(value: str) -> str:
    """Format the game map's element message.

    :param value: The value to put inside the message
    :type value: str
    :returns: The formatted message
    """
    return 'Click on the {0} center (as best as you can)'.format(value)


if __name__ == '__main__':
    SAMPLE_IMAGES_PATH = os.path.realpath(sys.argv[1])
    world_item_detector = WorldItemsManualDetector(SAMPLE_IMAGES_PATH)
    world_item_detector.iterate_images()
