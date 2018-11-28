from billing.drivers import BillingStripeDriver

class BillingFactory:

    @staticmethod
    def make(driver):
        if driver == 'stripe':
            return BillingStripeDriver()