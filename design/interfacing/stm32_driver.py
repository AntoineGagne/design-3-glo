import struct
import serial
import math
from threading import Thread
from design.interfacing.utils import detect_serial

from design.pathfinding.antenna_information import AntennaInformation


class Commands:
    TRANSLATE = 0x0000
    ROTATE = 0x0001
    FLASH_GREEN_LED = 0x0002
    ENABLE_RED_LED = 0x0003
    ENABLE_ADC = 0x0004
    DECODE_MANCHESTER = 0x0005
    STOP = 0x0006
    RESET = 0x0007


class Response:
    STM_READY = 0x0008
    SIGNAL_STRENGTH = 0x0009
    SIGNAL_DATA = 0x000A
    TRANSLATION_FINISHED = 0X000B
    ROTATION_FINISHED = 0X000C
    DECODING_FAILED = 0x000D


class Constants:
    EMPTY_PARAM = 0x0000
    ENABLED = 0xFFFF
    DISABLED = 0x0000
    MASK_FIGURE = 0x0E
    MASK_ORIENTATION = 0x30
    MASK_ZOOM = 0x40


class Stm32Driver:

    def __init__(self):
        self.observers = []

        self.port = serial.Serial()
        self.port.baudrate = 19200
        self.port.timeout = 1
        self.command_format = "<HHHH"
        self.response_format = "<HHH"
        self.response_size = 6
        self.thread = Thread(target=self.run)
        self.port.port = detect_serial("USB")[0]
        self.port.open()
        self.is_running = True
        self.is_ready = False
        self.signal_strength = None
        self.antenna_information = None

        self.thread.start()

    def register_hardware_observer(self, observer):
        """ Registers a new observer.
        :param observer: Hardware observer"""
        self.observers.append(observer)

    def notify_all_observers(self, response_type):
        """ Notifies all observers of the completion of an operation. """
        for observer in self.observers:
            observer.notify(response_type)

    def translate_robot(self, dx, dy):
        """
        Send a translation command to the STM32.
        :param dx: The horizontal distance in mm.
        :param dy: The vertical distance in mm.
        """
        assert isinstance(dx, int)
        assert -32768 <= dx <= 32767, "The horizontal distance should be a 16 bits signed int."
        assert isinstance(dy, int)
        assert -32768 <= dy <= 32767, "The vertical distance should be a 16 bits signed int."
        print("DRIVER - SENDING TRANSLATE COMMAND")
        self.send_command(Commands.TRANSLATE, dx + 32768, dy + 32768)

    def rotate_robot(self, theta):
        """
        Send a rotation command to the STM32.
        :param theta: The angle in radians.
        """
        assert isinstance(theta, (int, float))
        assert -2 * math.pi <= theta <= 2 * math.pi, "The rotation angle should be in the range [-2Pi, 2Pi]."
        converted = int((theta + 2 * math.pi) * 100)
        print("DRIVER - SENDING ROTATE COMMAND")
        self.send_command(Commands.ROTATE, converted)

    def stop_robot(self):
        """
        Send a stop command to the STM32.
        """
        self.send_command(Commands.STOP)

    def reset_robot(self):
        """
        Send a reboot command to the STM32.
        """
        self.send_command(Commands.RESET)

    def enable_red_led(self, is_enabled):
        """
        Starts or stops the red led.
        :param is_enabled: A boolean. True: led enabled, False: led disabled.
        """
        assert isinstance(is_enabled, bool)
        if is_enabled:
            param = Constants.ENABLED
        else:
            param = Constants.DISABLED
        self.send_command(Commands.ENABLE_RED_LED, param)

    def flash_green_led(self, milliseconds):
        """
        Turn the green led on for a certain duration in milliseconds, then turn it back off.
        :param milliseconds: The duration in milliseconds.
        """
        assert isinstance(milliseconds, int)
        assert 0 <= milliseconds <= 65535, "The duration should be a 16 bits unsigned int."
        self.send_command(Commands.FLASH_GREEN_LED, milliseconds)

    def enable_sampling(self, is_enabled):
        """
        Starts or stops the Manchester signal strength measurement.
        :param is_enabled: A boolean. True: acquisition enabled, False: acquisition disabled.
        """
        assert isinstance(is_enabled, bool)
        if is_enabled:
            param = Constants.ENABLED
        else:
            param = Constants.DISABLED
        self.send_command(Commands.ENABLE_ADC, param)

    def decode_manchester(self):
        """
        Starts the Manchester signal decoding algorithm on the STM32.
        """
        self.send_command(Commands.DECODE_MANCHESTER)

    def send_command(self, command, param1=Constants.EMPTY_PARAM, param2=Constants.EMPTY_PARAM):
        checksum = (65536 - command - param1 - param2) % 65536
        packet = struct.pack(self.command_format, command, param1, param2, checksum)
        self.port.write(packet)

    def run(self):
        while self.is_running:
            if self.port.in_waiting >= self.response_size:
                data_array = self.port.read(self.response_size)
                try:
                    data_list = struct.unpack(self.response_format, data_array)
                    if self.validate_checksum(data_list):
                        if data_list[0] == Response.STM_READY:
                            self.is_ready = True
                        elif data_list[0] == Response.SIGNAL_STRENGTH:
                            self.signal_strength = data_list[1]
                            self.notify_all_observers(Response.SIGNAL_STRENGTH)
                        elif data_list[0] == Response.SIGNAL_DATA:
                            painting_number = (data_list[1] & Constants.MASK_FIGURE) >> 1
                            zoom = ((data_list[1] & Constants.MASK_ZOOM) >> 5) + 2
                            orientation = (360 - ((data_list[1] & Constants.MASK_ORIENTATION) >> 4) * 90) % 360
                            print("DRIVER IS BUILDING ANTENNA_INFO")
                            self.antenna_information = AntennaInformation()
                            self.antenna_information.painting_number = painting_number
                            self.antenna_information.zoom = zoom
                            self.antenna_information.orientation = orientation
                            self.notify_all_observers(Response.SIGNAL_DATA)
                        elif data_list[0] == Response.DECODING_FAILED:
                            self.antenna_information = AntennaInformation()
                            self.antenna_information.painting_number = None
                            self.antenna_information.zoom = None
                            self.antenna_information.orientation = None
                            self.notify_all_observers(Response.SIGNAL_DATA)
                        elif data_list[0] == Response.TRANSLATION_FINISHED:
                            self.notify_all_observers(Response.TRANSLATION_FINISHED)
                        elif data_list[0] == Response.ROTATION_FINISHED:
                            self.notify_all_observers(Response.ROTATION_FINISHED)
                        else:
                            print("Invalid opcode")
                except struct.error:
                    # This error can occur if we don't read enough bytes on the serial port or if the packet format is
                    # incorrect.
                    print("Invalid received packet")
        self.port.close()

    def close(self):
        self.is_running = False
        self.thread.join()

    @staticmethod
    def validate_checksum(data_list):
        checksum = sum(data_list) % 65536
        if checksum == 0:
            return True
        else:
            print("Invalid Checksum : expected = 0, calculated = {}".format(checksum))
            return False
