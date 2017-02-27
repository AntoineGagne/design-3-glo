"""Constants used by the modules in the `vision` module."""

import itertools
import operator

# These were taken from the image samples
PAINTING_FRAME_LOWER_GREEN = (35.1, 108, 69.75)
PAINTING_FRAME_UPPER_GREEN = (65.45, 255, 154)

# These were taken from the image samples
LOWER_WHITE = (0, 0, 107.5)
UPPER_WHITE = (170.5, 100, 200)

# The dimension of the warped images (chosen arbitrarily)
WARPED_IMAGE_DIMENSIONS = (300, 300)
WARPED_IMAGE_CORNERS = [[0, 0], [300, 0], [300, 300], [0, 300]]

# The real dimensions in centimeters
REAL_PAINTING_DIMENSION = (14.8, 14.8)
REAL_DRAWING_AREA_DIMENSION = (59.7, 59.7)

# The ratios with the warped dimensions
# Given as: (x, y)
PAINTING_DIMENSION_RATIO = tuple(itertools.starmap(operator.truediv,
                                                   zip(REAL_PAINTING_DIMENSION,
                                                       WARPED_IMAGE_DIMENSIONS)))
DRAWING_DIMENSION_RATIO = tuple(itertools.starmap(operator.truediv,
                                                  zip(REAL_PAINTING_DIMENSION,
                                                      WARPED_IMAGE_DIMENSIONS)))

ROBOT_HEIGHT = 30  # TODO get real value
OBSTACLE_HEIGHT = 41  # in cm
LOWER_TRIANGLE_BOX_SIZE = 28
HIGHER_TRIANGLE_BOX_SIZE = 80
WORLD_INTRINSIC_MATRIX = []
ONBOARD_INTRINSIC_MATRIX = []
OPTIMIZED_CAMERA_VALUES = [[],
                           [50, 47, 175, 368, 20],
                           [50, 47, 175, 368, 20],
                           [50, 47, 175, 368, 20],
                           [50, 47, 175, 368, 20],
                           [50, 47, 175, 368, 20],
                           [50, 47, 175, 368, 20]]

# drawing zone borders : green range
MIN_GREEN = [45, 110, 120]
MAX_GREEN = [80, 255, 255]

MIN_MAGENTA = [160, 100, 100]
MAX_MAGENTA = [170, 255, 255]

DRAWING_ZONE_MIN_AREA = 100000

OBSTACLE_MIN_RADIUS = 20
OBSTACLE_MAX_RADIUS = 60

MIN_ROBOT_CIRCLE_RADIUS = 5
