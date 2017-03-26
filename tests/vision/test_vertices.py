import re
import math

import cv2
import numpy as np

from tests.utils import list_files, ImageAssertionHelper
import design.vision.vertices as vertices
import design.vision.exceptions as exceptions


SAMPLE_IMAGES = list(list_files('samples'))
CONTOURS_NUMBER_BY_ONBOARD_IMAGES_NAME_PATTERNS = {
    re.compile('boot.*'): np.array([[[140, 28]],
                                    [[245, 30]],
                                    [[243, 253]],
                                    [[192, 253]],
                                    [[191, 213]],
                                    [[151, 253]],
                                    [[37, 251]],
                                    [[38, 211]],
                                    [[139, 130]]]),
    re.compile('/arrow.*'): np.array([[[237, 38]],
                                      [[152, 120]],
                                      [[265, 190]],
                                      [[197, 263]],
                                      [[121, 152]],
                                      [[46, 222]],
                                      [[51, 39]]]),
    re.compile('inverted_arrow.*'): np.array([[[261, 45]],
                                              [[262, 232]],
                                              [[179, 151]],
                                              [[108, 264]],
                                              [[34, 194]],
                                              [[146, 120]],
                                              [[75, 45]]]),
    re.compile('hat.*'): np.array([[[123, 60]],
                                   [[149, 78]],
                                   [[176, 61]],
                                   [[205, 180]],
                                   [[242, 171]],
                                   [[230, 227]],
                                   [[68, 224]],
                                   [[50, 171]],
                                   [[88, 178]]]),
    re.compile('m(_\d+)?\.(jpg|png)'): np.array([[[283, 226]],
                                                 [[208, 226]],
                                                 [[201, 134]],
                                                 [[149, 186]],
                                                 [[98, 136]],
                                                 [[88, 227]],
                                                 [[16, 223]],
                                                 [[84, 69]],
                                                 [[213, 68]]]),
    re.compile('house.*'): np.array([[[40, 153]],
                                     [[147, 46]],
                                     [[182, 80]],
                                     [[239, 80]],
                                     [[240, 137]],
                                     [[254, 151]],
                                     [[254, 254]],
                                     [[155, 255]],
                                     [[155, 171]],
                                     [[106, 170]],
                                     [[104, 254]],
                                     [[40, 255]]]),
    re.compile('cat.*'): np.array([[[280, 29]],
                                   [[242, 111]],
                                   [[262, 208]],
                                   [[152, 260]],
                                   [[32, 211]],
                                   [[46, 128]],
                                   [[22, 34]],
                                   [[86, 79]],
                                   [[132, 55]],
                                   [[187, 77]]]),
    re.compile('cross.*'): np.array([[[205, 38]],
                                     [[264, 95]],
                                     [[209, 150]],
                                     [[264, 206]],
                                     [[208, 261]],
                                     [[153, 207]],
                                     [[96, 261]],
                                     [[37, 204]],
                                     [[93, 150]],
                                     [[37, 92]],
                                     [[95, 39]],
                                     [[151, 93]]]),
    re.compile('chess_piece.*'): np.array([[[149, 28]],
                                           [[208, 65]],
                                           [[208, 106]],
                                           [[183, 121]],
                                           [[203, 235]],
                                           [[245, 272]],
                                           [[50, 269]],
                                           [[96, 226]],
                                           [[116, 121]],
                                           [[91, 106]],
                                           [[91, 64]]]),
    re.compile('polygon.*'): np.array([[[263, 127]],
                                       [[214, 229]],
                                       [[75, 236]],
                                       [[79, 187]],
                                       [[40, 123]],
                                       [[139, 138]],
                                       [[137, 65]],
                                       [[204, 63]],
                                       [[217, 134]]]),
    re.compile('star.*'): np.array([[[271, 113]],
                                    [[193, 163]],
                                    [[220, 242]],
                                    [[149, 194]],
                                    [[80, 243]],
                                    [[106, 162]],
                                    [[41, 110]],
                                    [[123, 111]],
                                    [[149, 28]],
                                    [[177, 111]]])
}


def test_that_given_images_with_geometric_figure_when_find_geometric_figure_vertices_then_vertices_are_found():
    image_assertion_helper = ImageAssertionHelper(0.11)
    assert_equal = image_assertion_helper.assert_equal
    vertices_finder = vertices.VerticesFinder(vertices.HighFrequencyFilter(),
                                              0.008)
    for pattern, vertices_number in CONTOURS_NUMBER_BY_ONBOARD_IMAGES_NAME_PATTERNS.items():
        for image in filter(pattern.search, SAMPLE_IMAGES):
            opened_image = cv2.imread(image, 1)
            found_vertices = __find_vertices_wrapper(vertices_finder, opened_image)
            error_coefficient = cv2.matchShapes(found_vertices.coordinates, vertices_number, 1, 0.0) if found_vertices else math.inf
            assert_equal(
                error_coefficient <= 0.06,
                image_name=image,
                error_coefficient=error_coefficient
            )
    image_assertion_helper.assert_below_threshold()


def __find_vertices_wrapper(vertices_finder, image):
    vertices = None
    try:
        vertices = vertices_finder.find_vertices(image)
    except exceptions.VerticesNotFound:
        pass
    except exceptions.PaintingFrameNotFound:
        pass
    return vertices
