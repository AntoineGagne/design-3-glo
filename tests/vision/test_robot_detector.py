import json
import os.path as path

import cv2
import pytest

from tests.utils import (ImageAssertionHelper,
                         list_files)
from design.vision.robot_detector import RobotDetector

WORLD_CAMERA_SAMPLES_PATH = path.join('samples', 'world_camera_samples')
SAMPLE_IMAGES = list_files(WORLD_CAMERA_SAMPLES_PATH,
                           lambda filename: filename.endswith(('.png',
                                                               '.jpg',
                                                               '.jpeg')))
SAMPLE_JSON = list_files(WORLD_CAMERA_SAMPLES_PATH,
                         lambda filename: filename.endswith(('.json')))
SAMPLES_IMAGES_AND_JSON = dict(zip(SAMPLE_IMAGES, SAMPLE_JSON))


@pytest.mark.skip(reason='The images can not be extracted')
def test_that_given_images_with_robot_when_find_robot_position_then_robot_position_is_found():
    image_assertion_helper = ImageAssertionHelper(0.12)
    robot_detector = RobotDetector()
    for image_path, json_path in SAMPLES_IMAGES_AND_JSON.items():
        image = cv2.imread(image_path)
        found_robot_position, _ = robot_detector.detect_robot(image)
        with open(json_path) as data_file:
            data = json.load(data_file)
            robot_position = data["robot"]
        image_assertion_helper.assert_close(
            found_robot_position,
            robot_position,
            image_path=image_path,
            found_robot_position=found_robot_position,
            expected_robot_position=robot_position
        )
    image_assertion_helper.assert_below_threshold()
