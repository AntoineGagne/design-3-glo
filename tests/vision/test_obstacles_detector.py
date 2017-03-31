import json
import os.path as path

import pytest

from design.vision.obstacles_detector import ObstaclesDetector
from tests.utils import (ImageAssertionHelper,
                         list_files)


WORLD_CAMERA_SAMPLES_PATH = path.join('samples', 'world_camera_samples')
SAMPLE_IMAGES = list_files(WORLD_CAMERA_SAMPLES_PATH,
                           lambda filename: filename.endswith(('.png',
                                                               '.jpg',
                                                               '.jpeg')))
SAMPLE_JSON = list_files(WORLD_CAMERA_SAMPLES_PATH,
                         lambda filename: filename.endswith(('.json')))
SAMPLES_IMAGES_AND_JSON = dict(zip(SAMPLE_IMAGES, SAMPLE_JSON))


@pytest.mark.skip(reason='The images can not be extracted')
def test_that_given_images_with_obstacles_when_find_obstacles_positions_then_all_obstacles_positions_are_found():
    image_assertion_helper = ImageAssertionHelper(0.12)  # 0.12 is the maximum error percentage (so min is 87)
    obstacles_detector = ObstaclesDetector()

    for image_path, json_path in SAMPLES_IMAGES_AND_JSON.items():

        obstacles_coordinates = []
        found_obstacles_coordinates = []

        # get found coordinates
        obstacles_detector.refresh_frame(image_path)
        found_obstacles_information = obstacles_detector.calculate_obstacles_information()
        if found_obstacles_information is not None:
            for obstacle_information in found_obstacles_information:
                found_obstacles_coordinates.append(obstacle_information[0])

        # get coordinates to test against
        with open(json_path) as data_file:
            data = json.load(data_file)
            for obstacle_key in ["obstacle1", "obstacle2", "obstacle3"]:
                if obstacle_key in data.keys():
                    obstacles_coordinates.append(data[obstacle_key])

        # no need to compare coordinates if not all coordinates are found
        image_assertion_helper.assert_equal(
            len(found_obstacles_coordinates) == len(obstacles_coordinates),
            image_path=image_path,
            found_coordinates_number=len(found_obstacles_coordinates),
            expected_coordinates_number=len(obstacles_coordinates)
        )

        image_assertion_helper.assert_all_close(
            found_obstacles_coordinates,
            obstacles_coordinates,
            image_path=image_path,
            found_coordinates=found_obstacles_coordinates,
            expected_coordinates=obstacles_coordinates
        )
    image_assertion_helper.assert_below_threshold()
