class LedController:
    def reset(self):
        pass

    def set(self, id):
        pass


class PrintoutLedController(LedController):
    def reset(self):
        print('Reset')

    def set(self, id):
        print('set {}'.format(id))

if __name__ == "__main__":
    led_controller = PrintoutLedController()
    led_controller.reset()
    led_controller.set(1)
