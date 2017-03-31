import time
from design.interfacing.pen_driver import PenDriver


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
