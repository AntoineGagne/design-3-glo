"""Constants used by the modules in the `vision` module."""

import itertools
import operator

# These were taken from the image samples
LOWER_GREEN = (35.1, 108, 69.75)
UPPER_GREEN = (65.45, 255, 154)

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
# TODO get real values
ROBOT_HEIGHT = 30
OBSTACLE_HEIGHT = 30
WORLD_INTRINSIC_MATRIX = []
WORLD_EXTRINSIC_MATRIX = []
ONBOARD_INTRINSIC_MATRIX = []
WORLD_COMPLETE_MATRIX = []

# this is the default port
CAMERA_PORT = 0
DEFAULT_CAMERA_VALUES = [[] for i in range(7)]
OPTIMIZED_CAMERA_VALUES = [[], [], [], [-1.0, -1.0, -1.0, 640.0, 480.0, 0.0, -466162819.0, -1.0, -1.0, -1.0, 20.0, 255.0, 56.0, -1715724592.0, 141.0, -9.0, -1.0, 92.0, -1.0, -1715724592.0, 191.0, -1.0]]
