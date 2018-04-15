from masonite.managers.Manager import Manager


from pydoc import locate
class BillingManager(Manager):

    def create_driver(self, driver):
        return locate('billing.drivers.Billing{0}Driver.Billing{0}Driver'.format(driver.capitalize()))()
