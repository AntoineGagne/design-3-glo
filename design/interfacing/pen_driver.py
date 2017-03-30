import serial
import time
from threading import Thread
from design.interfacing.utils import detect_serial


class PenDriver:

    def __init__(self, channel=0, low_position=5000, high_position=4000, speed=0, acceleration=0):
        self.pen_channel = channel
        self.low_position = low_position
        self.high_position = high_position
        self._is_low = False
        port = detect_serial("ACM")[0]
        print("Pololu on port: " + port)
        self.usb = serial.Serial(port)
        self.PololuCmd = chr(0xaa) + chr(0xc)
        self.Targets = [0] * 24
        self.Mins = [0] * 24
        self.Maxs = [0] * 24
        self._set_range(self.pen_channel, 2000, 8000)
        self._set_speed(self.pen_channel, speed)
        self._set_acceleration(self.pen_channel, acceleration)
        self.raise_pen()
        self.thread = Thread(target=self._run)
        self._is_running = True
        self.thread.start()

    def lower_pen(self):
        self._set_target(self.pen_channel, self.low_position)
        self._is_low = True

    def raise_pen(self):
        self._set_target(self.pen_channel, self.high_position)
        self._is_low = False

    def is_moving(self):
        return self._is_moving(self.pen_channel)

    def close(self):
        self._is_running = False
        self.thread.join()
        self.usb.close()

    def _set_range(self, channel, min_position, max_position):
        self.Mins[channel] = min_position
        self.Maxs[channel] = max_position

    def _set_target(self, channel, target):
        # if Min is defined and Target is below, force to Min
        if self.Mins[channel] > 0 and target < self.Mins[channel]:
            target = self.Mins[channel]
        # if Max is defined and Target is above, force to Max
        if target > self.Maxs[channel] > 0:
            target = self.Maxs[channel]
        self._send_command(0x04, channel, target)
        # Record Target value
        self.Targets[channel] = target

    def _set_speed(self, channel, speed):
        self._send_command(0x07, channel, speed)

    def _set_acceleration(self, channel, acceleration):
        self._send_command(0x09, channel, acceleration)

    def _get_position(self, channel):
        self._send_command(0x10, channel)
        lsb = ord(self.usb.read())
        msb = ord(self.usb.read())
        return (msb << 8) + lsb

    def _is_moving(self, channel):
        if self.Targets[channel] > 0:
            target = self.Targets[channel]
            if not target - 5 < self._get_position(channel) < target + 5:
                return True
        return False

    def _send_command(self, command, channel, param=None):
        if param is not None:
            lsb = param & 0x7f  # 7 bits for least significant byte
            msb = (param >> 7) & 0x7f  # shift 7 and take next 7 bits for msb
            # Send Pololu intro, device number, command, channel, and parameter lsb/msb
            cmd = self.PololuCmd + chr(command) + chr(channel) + chr(lsb) + chr(msb)
        else:
            cmd = self.PololuCmd + chr(command) + chr(channel)
        self.usb.write(cmd.encode('latin-1'))

    def _run(self):
        while self._is_running:
            time.sleep(60)
            if self._is_low:
                self.low_position += 100
                self.lower_pen()


if __name__ == "__main__":
    driver = PenDriver()
    print("init done")
    print(driver._get_position(0))
    time.sleep(5)
    driver.lower_pen()
    print(driver._get_position(0))
    time.sleep(25)
    driver.raise_pen()
    driver.close()
    print("closing")
