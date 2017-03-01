import cv2
import os
import json


class WorldItemsManualDetector:
    def __init__(self, directory_path):

        self.images_directory_path = directory_path
        self.coordinates = {"upper-left": (0, 0)}
        self.key = "upper-left"

        self.image_path = None

        cv2.namedWindow("image")
        cv2.setMouseCallback("image", self.printer)

        self.image_looper()

    def image_looper(self):
        for filename in os.listdir(self.images_directory_path):
            if filename.endswith(".jpg", ".png"):
                image_path = os.path.join(self.images_directory_path, filename)
                self.image_path = image_path
                self.reset_data()
                self.enter_loop()
                self.record_data()
        print("THIS IS THE END ! THANK YOU !")

    # define mouse callback function
    def printer(self, event, x, y):
        if event == cv2.EVENT_LBUTTONDOWN:
            print("the coordinates you have set for {} are ({}, {})".format(self.key, x, y))
            self.coordinates[self.key] = (x, y)

    def reset_data(self):
        self.coordinates = {"upper-left": (0, 0)}

    def enter_loop(self):
        while True:
            loaded_image = cv2.imread(self.image_path)
            cv2.imshow('image', loaded_image)
            k = cv2.waitKey(33)  # 0xFF for masking last 8 bits of value
            if k == 32:  # SPACE key
                break
            elif k == 49:  # 1 key
                print("click on upper-left corner of the drawing zone")
                self.key = "upper-left"
            elif k == 50:  # 2 key
                print("click on upper-right corner of the drawing zone")
                self.key = "upper-right"
            elif k == 51:  # 3 key
                print("click on lower-left corner of the drawing zone")
                self.key = "lower-left"
            elif k == 52:  # 4 key
                print("click on lower-right corner of the drawing zone")
                self.key = "lower-right"
            elif k == 48:  # 0 key
                print("click on first obstacle center (as best as you can)")
                self.key = "obstacle1"
            elif k == 57:  # 9 key
                print("click on second obstacle center (as best as you can)")
                self.key = "obstacle2"
            elif k == 56:  # 8 key
                print("click on third obstacle center (as best as you can)")
                self.key = "obstacle3"
            elif k == 114:  # r key
                print("click on robot center (as best as you can)")
                self.key = "robot"
            elif k == 101:  # e key
                if self.key in self.coordinates:
                    print("Erased {} coordinates".format(self.key))
                    self.coordinates.pop(self.key)
                else:
                    print("Nothing erased, there were no coordinates found for {}".format(self.key))
            elif k == -1:  # normally -1 returned,so don't print it
                continue
            else:
                print(k)  # else print its value

    def record_data(self):
        with open('{}.json'.format(self.image_path), 'w', encoding='utf-8') as outfile:
            json.dump(self.coordinates, outfile)


if __name__ == '__main__':
    SAMPLE_IMAGES_PATH = os.path.realpath('..\..\world_camera_samples')
    WorldItemsManualDetector(SAMPLE_IMAGES_PATH)
