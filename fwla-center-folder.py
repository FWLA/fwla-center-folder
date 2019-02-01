from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import logging


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


class I2CLedController(LedController):
    def reset(self):
        # TODO Implement I2C reset
        logging.info('Reset')

    def set(self, id):
        # TODO Implement I2C set
        logging.info('set {}'.format(id))

# Controller for WS2812 connected LEDs


class WS2812LedController(LedController):
    def reset(self):
        # TODO Implement WS2812 reset
        logging.info('Reset')

    def set(self, id):
        # TODO Implement WS2812 set
        logging.info('set {}'.format(id))


# BASIC OPTIONS
logging.basicConfig(level=logging.INFO)

TEST_ENV = 'http://localhost:8080/v1/display'
PROD_ENV = 'http://fwla-center.ffwlampertheim.local/api/v1/display'

url = TEST_ENV

controller = LoggingLedController()


def job():
    try:
        r = requests.get(url)
        data = r.json()
        if (data['state'] != 'OPERATION'):
            logging.debug('Not operation state.')
            controller.reset()
            return

        if 'operation' not in data:
            logging.debug('No operation.')
            controller.reset()
            return

        operation = data['operation']

        if 'realEstate' not in operation:
            logging.debug('No realEstate.')
            controller.reset()
            return

        realEstate = operation['realEstate']

        if 'folderAddress' not in realEstate:
            logging.debug('No folderAddress.')
            controller.reset()
            return

        folderAddress = int(realEstate['folderAddress'])
        controller.set(folderAddress)
    except:
        logging.warn('Exception when getting data.')
        controller.reset()


def init():
    logging.info('Starting process.')
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'interval', seconds=5)
    try:
        scheduler.start()
    except (KeyboardInterrupt):
        logging.info('Stopping process.')


if __name__ == "__main__":
    init()
