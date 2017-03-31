import cv2

from functools import wraps
import json
import math
import os
import sys
import textwrap

from design.vision.exceptions import PaintingFrameNotFound
import design.vision.contours as contours
import design.vision.transformations as transformations


def _exit_program():
    """Raise an exception that signals the end of the program.

    :raises ExitProgramException: Indicate the end of the program
    """
    raise ExitProgramException('\n\n{0}\n{1}'.format(
        _create_banner('Closing program...', '*'),
        'The program was successfully closed.')
    )


def _warp_image(image):
    """Perform an homography on an image.

    :param image: The image on which to perform the homography
    :returns: The warped image

    :raises PaintingFrameNotFound: If the painting's frame could not be found
    """
    painting_frame_finder = contours.PaintingFrameFinder()
    frame_vertices = painting_frame_finder.find_frame_coordinates(image)
    perspective_warper = transformations.PerspectiveWarper()
    return perspective_warper.change_image_perspective(image, frame_vertices)


def _create_banner(title: str, delimiter: str='=-') -> str:
    """Create a banner with the given title and the given delimiters.

    :param title: The title to display in the banner
    :type title: str
    :param delimiter: The delimiter to use
    :type delimiter: str
    :returns: The banner string
    :rtype: str
    """
    edge = delimiter * math.floor(80 / len(delimiter))
    spaces = ' ' * math.floor((80 - len(title)) / 2)
    return '{0}\n{1}{2}{1}\n{0}'.format(edge, spaces, title)


def print_banner(banner):
    """A decorator used to print a banner before calling a function.

    :param banner: The banner to print
    :type banner: str
    :returns: The wrapped wrapper function
    :rtype: function
    """
    def wrapped_print_banner(wrapped_function):
        """Wrap the given function so that it prints the banner when called.

        :param wrapped_function: The function to wrap
        :type wrapped_function: function
        :returns: The wrapper
        :rtype: function
        """
        @wraps(wrapped_function)
        def wrapper(*args, **kwargs):
            """Print the banner then call the wrapped function.

            :param args: Arbitrary parameters
            :param kwargs: Arbitrary keywords arguments
            :returns: The result of calling *wrapped_function* with *args* and
                      *kwargs*
            """
            print(banner)
            return wrapped_function(*args, **kwargs)
        return wrapper
    return wrapped_print_banner


class KeyEventHandler:
    """Handles event with the given callback."""

    def __init__(self, keycode: str, callback, description: str):
        """Initialize the handler."""
        self.keycode = ord(keycode)
        self.description = description
        self.text_wrapper = textwrap.TextWrapper(initial_indent=' ' * 25,
                                                 subsequent_indent=' ' * 26,
                                                 width=79)
        self.callback = callback

    def __call__(self, *args, **kwargs):
        """Process the event with the callback.

        :param args: An arbitrary number of parameters
        :param kwargs: Arbitrary keyword parameters
        :returns: The same value as the callback
        """
        return self.callback(*args, **kwargs)

    def __str__(self) -> str:
        """Format the :class:Handler appropriately.

        :returns: The formatted :class:Handler
        :rtype: str
        """
        return '{0}{1}'.format(chr(self.keycode),
                               self.text_wrapper.fill(self.description))


class ExitProgramException(Exception):
    """Exception that is raised when the program is exited earlier."""
    pass


class VerticesIdentifier:
    """Identify vertices in images."""

    def __init__(self, images_directory_path):
        """Initialize the :class:VerticesIdentifier."""
        self.images_directory_path = images_directory_path
        self.vertices_by_image_name = {}
        self.coordinates = []
        self._initialize_callback()
        self.keyboard_handlers = {}
        self._initialize_keyboard_handlers()

    def _initialize_callback(self):
        """Initialize the mouse callback."""
        cv2.namedWindow('Vertices Identifier')
        cv2.setMouseCallback('Vertices Identifier',
                             self._add_coordinates)

    def _initialize_keyboard_handlers(self):
        """Initialize the keyboard handlers."""
        handlers = [KeyEventHandler('d',
                                    self._remove_coordinates,
                                    'Remove the latest entered coordinates if '
                                    'the list of coordinates is not empty. '
                                    'Otherwise, do nothing.'),
                    KeyEventHandler('h',
                                    self._display_help,
                                    'Display this message.'),
                    KeyEventHandler('q',
                                    _exit_program,
                                    'Exit the program without completing the '
                                    'task. Caution: it will not prompt for '
                                    'confirmation.')]
        for handler in handlers:
            self.keyboard_handlers[handler.keycode] = handler

    def _add_coordinates(self, event: int, x: int, y: int, *args):
        """Add the given coordinates to the list of coordinates.

        :param event: The current GUI event
        :type event: int
        :param x: The *x* coordinate
        :type x: int
        :param y: The *y* coordinate
        :type y: int
        :param args: An arbitrary number of parameters
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            print('Added ({0}, {1}) coordinates'.format(x, y))
            self.coordinates.append([[x, y]])

    def _remove_coordinates(self):
        """Remove the latest coordinates."""
        message = 'There were no coordinates to remove.'
        if self.coordinates:
            message = 'Removed {0} coordinates'.format(self.coordinates.pop())

        return message

    def iterate_images(self):
        """Iterate the images and allow interactions with the GUI.

        :raises ExitProgramException: An exception that indicates that the user
                                      wants to quit
        """
        print(self._display_help())
        for filename in os.listdir(self.images_directory_path):
            if filename.endswith(('.jpg', '.png')):
                try:
                    self._process_image(filename)
                except PaintingFrameNotFound:
                    continue

    def _process_image(self, filename: str):
        """Process the image and its vertices.

        :param filename: The file's name of the image
        :type filename: str
        """
        print('\n{0}'.format(_create_banner(filename, delimiter='-')))
        image_path = os.path.join(self.images_directory_path,
                                  filename)
        image = cv2.imread(image_path, 1)
        warped_image = _warp_image(image)
        self._process_vertices(filename, warped_image)

    def _process_vertices(self, filename: str, warped_image):
        """Identify vertices and add them to the list.

        :param filename: The file's name of the image
        :type filename: str
        :param warped_image: The image with an applied homography
        """
        self._identify_vertices(warped_image)
        self.vertices_by_image_name[filename] = self.coordinates
        self.coordinates = []

    def _identify_vertices(self, image):
        """Allow the user to identify vertices.

        :param image: The image in which to identify vertices
        """
        keycode = -1
        while keycode != ord('e'):
            cv2.imshow('Vertices Identifier', image)
            keycode = cv2.waitKey()
            if keycode in self.keyboard_handlers:
                print(self.keyboard_handlers[keycode]())
            else:
                continue

    def save_identified_vertices(self):
        """Save the identified vertices to a JSON file."""
        file_path = os.path.join(self.images_directory_path, 'vertices.json')
        with open(file_path, 'w', encoding='utf-8') as output_file:
            json.dump(self.vertices_by_image_name,
                      output_file,
                      sort_keys=True,
                      indent=4)

    @print_banner(_create_banner('Controls'))
    def _display_help(self) -> str:
        """Display a message with information about the various controls.

        :returns: A string containing information about the various controls
        :rtype: str
        """
        message = '\n'.join(
            ('\nTo enter the coordinates, just click with your mouse on a '
             'vertex.',
             'e{0}End the coordinates registering for the current '
             'image.'.format(' ' * 25))
        )
        return '{0}\n{1}'.format(
            message,
            '\n'.join(
                map(str, self.keyboard_handlers.values())
            )
        )


if __name__ == '__main__':
    SAMPLE_IMAGES_PATH = os.path.realpath(sys.argv[1])
    vertices_identifier = VerticesIdentifier(SAMPLE_IMAGES_PATH)
    try:
        vertices_identifier.iterate_images()
        vertices_identifier.save_identified_vertices()
    except ExitProgramException as exception:
        print('\n'.join(exception.args))
