from masonite.configuration import config


class Billing:

    def __init__(self, application):
        self.application = application
        self.drivers = {}
        self.drivers_config = {}
        self.options = {}

    def add_driver(self, name, driver):
        self.drivers.update({name: driver})

    def get_driver(self, name=None):
        if name is None:
            name = config("billing.drivers.default")
        driver = self.drivers[name]
        return driver.set_options(config(f"billing.drivers.{name}"))
