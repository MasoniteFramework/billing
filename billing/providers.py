""" A BillingProvider Service Provider """
from masonite.provider import ServiceProvider
from billing.commands.InstallCommand import InstallCommand


class BillingProvider(ServiceProvider):

    wsgi = False

    def register(self):
        self.app.bind('BillingInstallCommand', InstallCommand())

    def boot(self):
        pass
