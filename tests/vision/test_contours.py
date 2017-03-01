import re

import cv2

from tests.utils import list_files, ImageAssertionHelper
import design.vision.contours as contours

SAMPLE_IMAGES = list(list_files('samples'))
CONTOURS_NUMBER_BY_ONBOARD_IMAGES_NAME_PATTERNS = (
    re.compile('boot.*'),
    re.compile('^arrow.*'),
    re.compile('^inverted_arrow.*'),
    re.compile('hat.*'),
    re.compile('m(_\d+)?\.(jpg|png)'),
    re.compile('house.*'),
    re.compile('cat.*'),
    re.compile('cross.*'),
    re.compile('chess_piece.*'),
    re.compile('polygon.*'),
    re.compile('star.*'),
)


def test_that_given_an_image_with_green_square_when_find_green_square_coordinates_then_coordinates_are_found():
    image_assertion_helper = ImageAssertionHelper(0.01)
    painting_frame_finder = contours.PaintingFrameFinder()
    find_frame_coordinates = painting_frame_finder.find_frame_coordinates
    assert_equal = image_assertion_helper.assert_equal
    for pattern in CONTOURS_NUMBER_BY_ONBOARD_IMAGES_NAME_PATTERNS:
        for image in filter(pattern.search, SAMPLE_IMAGES):
            opened_image = cv2.imread(image, 1)
            contours_number = 0
            try:
                frame_coordinates = find_frame_coordinates(opened_image)
                contours_number = len(frame_coordinates)
            except:
                continue
            finally:
                assert_equal(contours_number == 4,
                             image_name=image,
                             contours_number_found=contours_number)
    image_assertion_helper.assert_below_threshold()
