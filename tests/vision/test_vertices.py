import re

import cv2

from tests.utils import list_files, ImageAssertionHelper
import design.vision.vertices as vertices


SAMPLE_IMAGES = list(list_files('samples'))
CONTOURS_NUMBER_BY_ONBOARD_IMAGES_NAME_PATTERNS = {
    re.compile('boot.*'): 9,
    re.compile('arrow.*'): 7,
    re.compile('hat.*'): 9,
    re.compile('m(_\d+)?\.(jpg|png)'): 9,
    re.compile('house.*'): 12,
    re.compile('cat.*'): 10,
    re.compile('cross.*'): 12,
    re.compile('chess_piece.*'): 11,
    re.compile('polygon.*'): 9
}


DEFAULT_SEARCH_VERTICES_OBJECTS = (
    vertices.VerticesFinder(vertices.WhiteBackgroundFilter()),
    vertices.VerticesFinder(vertices.HighFrequencyFilter(), 0.008),
    vertices.VerticesFinder(vertices.LaplacianFilter()),
    vertices.VerticesFinder(vertices.AdaptiveThresholdingFilter()),
    vertices.VerticesFinder(vertices.HsvColorspaceFilter()),
    vertices.VerticesFinder(vertices.OtsuBinarizationFilter())
)


def test_that_given_images_with_geometric_figure_when_find_geometric_figure_vertices_then_vertices_are_found():
    image_assertion_helper = ImageAssertionHelper(0.12)
    for pattern, vertices_number in CONTOURS_NUMBER_BY_ONBOARD_IMAGES_NAME_PATTERNS.items():
        for image in filter(pattern.search, SAMPLE_IMAGES):
            opened_image = cv2.imread(image, 1)
            found_vertices = vertices.find_geometric_figure_vertices(
                opened_image,
                *DEFAULT_SEARCH_VERTICES_OBJECTS
            )
            found_vertices_number = len(found_vertices.coordinates)
            image_assertion_helper.assert_equal(
                found_vertices_number,
                vertices_number,
                image_name=image,
                found_vertices_number=found_vertices_number,
                expected_vertices_number=vertices_number
            )
    image_assertion_helper.assert_below_threshold()
