import logging

LOGGER = logging.getLogger("interfacing_logger")
LOGGER.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('execution.log', 'w')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
LOGGER.addHandler(file_handler)


class ExecutionLogger():

    def __init__(self):
        self.logger = logging.getLogger("interfacing_logger")
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('execution.log', 'w')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def log(self, message):
        """ Logs a message to the file. """
        self.logger.debug(message)
