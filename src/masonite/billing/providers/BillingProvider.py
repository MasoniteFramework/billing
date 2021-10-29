""" A BillingProvider Service Provider """
from masonite.providers import Provider

from ..commands.InstallCommand import InstallCommand


class BillingProvider(Provider):

    def register(self):
        self.app.bind("BillingInstallCommand", InstallCommand())

    def boot(self):
        pass
