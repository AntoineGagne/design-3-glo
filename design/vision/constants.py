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