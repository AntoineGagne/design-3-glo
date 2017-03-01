import json
import os.path as path

from design.vision.drawing_zone_detector import DrawingZoneDetector
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


def test_that_given_images_with_drawing_zone_when_find_drawing_zone_then_drawing_zone_is_found():
    image_assertion_helper = ImageAssertionHelper(0.15)  # 0.15 is the maximum error percentage (so min is 87)
    drawing_zone_detector = DrawingZoneDetector()

    for image_path, json_path in SAMPLES_IMAGES_AND_JSON.items():

        drawing_zone_coordinates = []
        found_drawing_zone_coordinates = []

        # get found coordinates
        drawing_zone_detector.refresh_frame(image_path)
        found_coordinates = drawing_zone_detector.find_drawing_zone_vertices()

        if found_coordinates is not None:
            for coordinate in found_coordinates:
                found_drawing_zone_coordinates.append(coordinate)

        # get coordinates to test against
        with open(json_path) as data_file:
            data = json.load(data_file)
            for key in ["upper-right", "upper-left", "lower-right", "lower-left"]:
                if key in data.keys():
                    drawing_zone_coordinates.append(data[key])
            # print(drawing_zone_coordinates)

        # no need to compare coordinates if not all coordinates are found
        image_assertion_helper.assert_equal(
            len(found_drawing_zone_coordinates) == len(drawing_zone_coordinates),
            image_path=image_path,
            found_coordinates_number=len(found_drawing_zone_coordinates),
            expected_coordinates_number=len(drawing_zone_coordinates)
        )

        image_assertion_helper.assert_all_close(
            found_drawing_zone_coordinates,
            drawing_zone_coordinates,
            image_path=image_path,
            found_coordinates=found_drawing_zone_coordinates,
            expected_coordinates=drawing_zone_coordinates
        )
    image_assertion_helper.assert_below_threshold()
