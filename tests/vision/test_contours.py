import re

import cv2

from tests.utils import list_files
import design.vision.contours as contours

SAMPLE_IMAGES = list_files('samples')
CONTOURS_NUMBER_BY_ONBOARD_IMAGES_PATTERNS = {
    re.compile('boot.*'): 9,
    re.compile('arrow.*'): 7,
    re.compile('hat.*'): 9,
    re.compile('m.*'): 9,
    re.compile('house.*'): 12,
    re.compile('cat.*'): 10,
    re.compile('cross.*'): 12,
    re.compile('chess_piece.*'): 11,
    re.compile('polygon.*'): 9
}


def test_that_given_an_image_with_green_square_when_find_green_square_coordinates_then_coordinates_are_found():
    for pattern in CONTOURS_NUMBER_BY_ONBOARD_IMAGES_PATTERNS.keys():
        for image in filter(pattern.search, SAMPLE_IMAGES):
            opened_image = cv2.imread(image, 1)
            green_square_contours = contours.find_green_square_coordinates(opened_image)
            assert len(green_square_contours) == 4
