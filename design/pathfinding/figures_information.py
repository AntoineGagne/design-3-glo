""" Contains position and orientation to take the capture from """

MINIMUM_DISTANCE_BETWEEN_ROBOT_AND_FIGURE = 40
OUTER_FRAME_SIZE = 16.4
INNER_FRAME_SIZE = 14.8
SOUTHERN_AND_NORTHERN_WALL_DISTANCE_BETWEEN_OUTER_FRAMES = 8
WESTERN_WALL_DISTANCE_BETWEEN_OUTER_FRAMES = 8.9
DELTA_INCREMENT = 3


class FiguresInformation():
    """ Contains position and orientation to take the capture from """

    def __init__(self):
        self.figures = {}
        self.figures_backup_deltas = {}

        self.southeast_corner = (0, 0)
        self.southwest_corner = (0, 231)
        self.northwest_corner = (112, 231)
        self.northeast_corner = (112, 0)

        self.figures[0] = ((self.southwest_corner[0] + MINIMUM_DISTANCE_BETWEEN_ROBOT_AND_FIGURE,
                            self.southwest_corner[1] - (
                                2 * SOUTHERN_AND_NORTHERN_WALL_DISTANCE_BETWEEN_OUTER_FRAMES) - (
                            1.5 * OUTER_FRAME_SIZE)),
                           180)

        self.figures[1] = (
            (self.southwest_corner[0] + MINIMUM_DISTANCE_BETWEEN_ROBOT_AND_FIGURE, self.southwest_corner[1] - 20), 160)

        self.figures[2] = (
            (self.southwest_corner[0] + 20, self.southwest_corner[1] - MINIMUM_DISTANCE_BETWEEN_ROBOT_AND_FIGURE), 94)

        self.figures[3] = (
            (self.southwest_corner[0] + (1.5 * OUTER_FRAME_SIZE) + (2 * WESTERN_WALL_DISTANCE_BETWEEN_OUTER_FRAMES),
             self.southwest_corner[1] - MINIMUM_DISTANCE_BETWEEN_ROBOT_AND_FIGURE),
            90)

        self.figures[4] = (
            (self.northwest_corner[0] - (1.5 * OUTER_FRAME_SIZE) - (2 * WESTERN_WALL_DISTANCE_BETWEEN_OUTER_FRAMES),
             self.northwest_corner[1] - MINIMUM_DISTANCE_BETWEEN_ROBOT_AND_FIGURE),
            90)

        self.figures[5] = (
            (self.northwest_corner[0] - 20, self.northwest_corner[1] - MINIMUM_DISTANCE_BETWEEN_ROBOT_AND_FIGURE), 81)

        self.figures[6] = (
            (self.northwest_corner[0] - MINIMUM_DISTANCE_BETWEEN_ROBOT_AND_FIGURE, self.northwest_corner[1] - 20), 20)

        self.figures[7] = ((self.northwest_corner[0] - MINIMUM_DISTANCE_BETWEEN_ROBOT_AND_FIGURE,
                            self.northwest_corner[1] - (1.5 * OUTER_FRAME_SIZE) - (
                                2 * SOUTHERN_AND_NORTHERN_WALL_DISTANCE_BETWEEN_OUTER_FRAMES)),
                           0)

        self.figures_backup_deltas[0] = [(0, -DELTA_INCREMENT), (0, 2 * DELTA_INCREMENT), (0, -DELTA_INCREMENT)]
        self.figures_backup_deltas[1] = [(0, DELTA_INCREMENT), (0, DELTA_INCREMENT), (0, -(2 * DELTA_INCREMENT))]
        self.figures_backup_deltas[2] = [(-DELTA_INCREMENT, 0), (-DELTA_INCREMENT, 0), (0, 2 * DELTA_INCREMENT)]
        self.figures_backup_deltas[3] = [(-DELTA_INCREMENT, 0), (2 * DELTA_INCREMENT, 0), (-DELTA_INCREMENT, 0)]
        self.figures_backup_deltas[4] = [(-DELTA_INCREMENT, 0), (2 * DELTA_INCREMENT, 0), (-DELTA_INCREMENT, 0)]
        self.figures_backup_deltas[5] = [(DELTA_INCREMENT, 0), (DELTA_INCREMENT, 0), (-DELTA_INCREMENT, 0)]
        self.figures_backup_deltas[6] = [(0, DELTA_INCREMENT), (0, DELTA_INCREMENT), (0, -DELTA_INCREMENT)]
        self.figures_backup_deltas[7] = [(0, -DELTA_INCREMENT), (0, 2 * DELTA_INCREMENT), (0, -DELTA_INCREMENT)]

    def compute_positions(self, southeast_corner, southwest_corner,
                          northwest_corner, northeast_corner):
        """ Executes final computation of figure positions """

        self.southeast_corner = southeast_corner
        self.southwest_corner = southwest_corner
        self.northwest_corner = northwest_corner
        self.northeast_corner = northeast_corner

        print("Figures: {0}".format(self.figures))

    def get_position_to_take_figure_from(self, figure_index):
        """ Returns the position of which the robot must attempt to travel
        towards to take the picture """
        return self.figures[figure_index][0]

    def get_orientation_to_take_figure_from(self, figure_index):
        """ Returns the orientation of which the robot must head towards
        in order to take the picture """
        return self.figures[figure_index][1]

    def get_figure_list_of_retries_movement_deltas(self, figure_index):
        """ Returns a list of translation vectors in-between which a capture
        can be attempted again. """
        return self.figures_backup_deltas[figure_index]
