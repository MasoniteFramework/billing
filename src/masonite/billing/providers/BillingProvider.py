from masonite.providers import Provider

from ..commands.InstallCommand import InstallCommand
from ..Billing import Billing
from ..drivers import BillingStripeDriver


class BillingProvider(Provider):

    def __init__(self, application):
        self.application = application

    def register(self):
        # billing = Billing(self.application).set_configuration(Config.get("mail.drivers"))
        billing = Billing(self.application)
        billing.add_driver("stripe", BillingStripeDriver(self.application))
        self.application.bind("billing", billing)

        self.application.make('commands').add(
            InstallCommand()
        )

    def boot(self):
        pass
