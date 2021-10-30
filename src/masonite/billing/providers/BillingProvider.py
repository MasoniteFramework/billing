""" A BillingProvider Service Provider """
from masonite.providers import Provider

from ..commands.InstallCommand import InstallCommand


class BillingProvider(Provider):

    def __init__(self, application):
        self.application = application

    def register(self):
        self.application.make('commands').add(
            InstallCommand()
        )

    def boot(self):
        pass
