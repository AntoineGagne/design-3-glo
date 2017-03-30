import glob
import sys
import serial


def detect_serial(port_type=""):
    """ Lists serial port names
    :raises EnvironmentError
        On unsopported or unknown platforms
    :returns:
        A list of the serial ports available on the system
    """
    assert isinstance(port_type, str)
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        if port_type == "":
            port_string = '/dev/tty[A-Za-z]*'
        else:
            port_string = '/dev/tty' + port_type + '*'
        ports = glob.glob(port_string)
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result
