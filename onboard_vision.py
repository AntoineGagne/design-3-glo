#! /usr/bin/env python
import sys

import cv2

from design.vision.vertices import (HighFrequencyFilter,
                                    VerticesFinder)


if __name__ == "__main__":
    image = cv2.imread(sys.argv[1], 1)
    finder = VerticesFinder(HighFrequencyFilter())
    figure = finder.find_vertices(image)
    cv2.drawContours(image, [figure.coordinates], -1, (255, 255, 255), 3)
    cv2.imshow('Contours', image)
    cv2.waitKey()
