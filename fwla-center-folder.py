import logging

import random
import requests
import board
import neopixel
import smbus2
from apscheduler.schedulers.blocking import BlockingScheduler


class LedController:
    def reset(self):
        pass

    def set(self, id):
        pass


class LoggingLedController(LedController):
    def reset(self):
        logging.info('Reset')

    def set(self, id):
        logging.info('set {}'.format(id))

# Controller for I2C connected LEDs


class I2CLedController(LoggingLedController):

    def __init__(self):
        self.bus = smbus2.SMBus(1)
        self.bus.write_byte_data(0x20, 0x00, 0x00)
        self.bus.write_byte_data(0x20, 0x01, 0x00)

    def reset(self):
        super(I2CLedController, self).reset()
        self.bus.write_byte_data(0x20, 0x14, 0x00)
        self.bus.write_byte_data(0x20, 0x15, 0x00)

    def set(self, id):
        super(I2CLedController, self).set(id)

        register = 0x14
        if id / 8 > 0:
            register = 0x15

        bitmask = id % 8

        self.bus.write_byte_data(0x20, register, bitmask)

# Controller for WS2812 connected LEDs


class WS2812LedController(LedController):

    def __init__(self, color):
        self._color = color
        self._pixels = neopixel.NeoPixel(board.D18, 144, auto_write=False)
        self._pixels.fill((0, 0, 0))
        self._pixels.show()

    def reset(self):
        super(WS2812LedController, self).reset()

        self._pixels.fill((0, 0, 0))
        self._pixels.show()

    def set(self, id):
        super(WS2812LedController, self).set(id)

        self._pixels.fill((0, 0, 0))
        self._pixels[id] = self._color
        self._pixels.show()


# BASIC OPTIONS
logging.basicConfig(level=logging.INFO)

TEST_ENV = 'http://192.168.0.199:8080/v1/display'
PROD_ENV = 'http://10.24.6.35/api/v1/display'

url = TEST_ENV

color = (0, 0, 255)
controller = WS2812LedController(color)


def job():
    address = get_active_address()
    if address < 0:
        controller.reset()
    else:
        controller.set(address)


def get_mock_address():
    return random.randint(-1, 100)


def get_active_address():
    try:
        r = requests.get(url, timeout=2)
        data = r.json()
        if (data['state'] != 'OPERATION'):
            logging.debug('Not operation state.')
            return -1

        if 'operation' not in data:
            logging.debug('No operation.')
            return -1

        operation = data['operation']

        if 'realEstate' not in operation:
            logging.debug('No realEstate.')
            return -1

        realEstate = operation['realEstate']

        if 'folderAddress' not in realEstate:
            logging.debug('No folderAddress.')
            return -1

        folderAddress = int(realEstate['folderAddress'])
        return folderAddress
    except Exception as e:
        logging.warn('Exception when getting data.')
        logging.warn(e)
        return -1


def init():
    logging.info('Starting process.')
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'interval', seconds=5)
    try:
        scheduler.start()
    except (KeyboardInterrupt):
        controller.reset()
        logging.info('Stopping process.')


if __name__ == "__main__":
    init()
